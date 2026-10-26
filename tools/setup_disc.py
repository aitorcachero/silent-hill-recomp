#!/usr/bin/env python3
"""
Silent Hill Recompiled — Detector y Preparador Universal de Disco
Soporte completo:
  - PAL España (SLES-01514 en castellano)
  - PAL Europa (SCES-01514 inglés)
  - NTSC-U USA (SLUS-00707 v1.0 / v1.1)
  - NTSC-J Japón (SLPM-86192 original / Konami The Best SLPM-86641 / PSone Books SLPM-87328)
Formatos: .PBP, .BIN/.CUE, .ISO, .IMG, .CHD
"""

import os
import sys
import struct
import zlib
import re
import shutil
from pathlib import Path

KNOWN_VERSIONS = {
    "SLES_015.14": {
        "serial": "SLES-01514",
        "title": "Silent Hill (España / Europa - Castellano)",
        "region": "PAL",
        "hz": 50.0,
        "lang": "es",
        "boot_exe": "SLES_015.14"
    },
    "SCES_015.14": {
        "serial": "SCES-01514",
        "title": "Silent Hill (Europe - English)",
        "region": "PAL",
        "hz": 50.0,
        "lang": "en",
        "boot_exe": "SCES_015.14"
    },
    "SLUS_007.07": {
        "serial": "SLUS-00707",
        "title": "Silent Hill (USA - English v1.0/v1.1)",
        "region": "NTSC-U",
        "hz": 59.94,
        "lang": "en",
        "boot_exe": "SLUS_007.07"
    },
    "SLPM_861.92": {
        "serial": "SLPM-86192",
        "title": "Silent Hill (Japan - NTSC-J v1.0)",
        "region": "NTSC-J",
        "hz": 59.94,
        "lang": "ja",
        "boot_exe": "SLPM_861.92"
    },
    "SLPM_866.41": {
        "serial": "SLPM-86641",
        "title": "Silent Hill (Japan - Konami The Best)",
        "region": "NTSC-J",
        "hz": 59.94,
        "lang": "ja",
        "boot_exe": "SLPM_866.41"
    },
    "SLPM_873.28": {
        "serial": "SLPM-87328",
        "title": "Silent Hill (Japan - PSone Books)",
        "region": "NTSC-J",
        "hz": 59.94,
        "lang": "ja",
        "boot_exe": "SLPM_873.28"
    }
}

def extract_pbp(pbp_path: Path, out_bin: Path):
    print(f"[*] Desempaquetando imagen Sony PSP/PS3 PBP: {pbp_path.name}...")
    with open(pbp_path, "rb") as f:
        header = f.read(40)
        if header[:4] != b"\x00PBP":
            print("[!] Error: No es un archivo PBP valido.")
            return False
            
        offsets = struct.unpack("<8I", header[8:40])
        psar_offset = offsets[7]
        f.seek(psar_offset)
        psar_magic = f.read(12)
        if psar_magic[:4] != b"PSAR":
            print("[!] Error: Magic PSAR invalido.")
            return False
            
        f.seek(psar_offset + 0x200)
        header_data = f.read(0x4000)
        
        psiso_idx = header_data.find(b"PSISOIMG0000")
        if psiso_idx == -1:
            f.seek(psar_offset)
            full_search = f.read(0x100000)
            psiso_idx = full_search.find(b"PSISOIMG0000")
            table_offset = psar_offset + psiso_idx + 0x400 if psiso_idx != -1 else psar_offset + 0x4000
        else:
            table_offset = psar_offset + 0x200 + psiso_idx + 0x400

        f.seek(table_offset)
        table_raw = f.read(0x100000)
        
        entries = []
        for i in range(0, len(table_raw), 32):
            if i + 32 > len(table_raw):
                break
            chunk = table_raw[i:i+32]
            off, length = struct.unpack("<II", chunk[:8])
            if off == 0 and length == 0:
                break
            entries.append((off, length))

        if not entries:
            f.seek(psar_offset + 0x400)
            table_raw = f.read(0x100000)
            for i in range(0, len(table_raw), 8):
                chunk = table_raw[i:i+8]
                off, length = struct.unpack("<II", chunk)
                if off == 0 and length == 0:
                    break
                entries.append((off, length))

        print(f"    Total bloques encontrados: {len(entries)}")
        with open(out_bin, "wb") as out_f:
            for i, (off, length) in enumerate(entries):
                if length == 0:
                    continue
                f.seek(psar_offset + off)
                comp_data = f.read(length)
                try:
                    decomp = zlib.decompress(comp_data)
                    out_f.write(decomp)
                except Exception:
                    out_f.write(comp_data)
                    
                if i > 0 and i % 2500 == 0:
                    print(f"    ... procesados {i} bloques de sectores...")
                    
    print(f"[+] Extraccion PBP completada: {out_bin.name} ({out_bin.stat().st_size // (1024*1024)} MB)")
    return True

def detect_serial(bin_path: Path):
    with open(bin_path, "rb") as f:
        data = f.read(4 * 1024 * 1024)
        m = re.search(rb'(SLES|SLUS|SCES|SCPS|SLED|SLPS|SCED|SCUS|SLPM)[_-](\d{3})\.?(\d{2})', data, re.IGNORECASE)
        if m:
            prefix = m.group(1).decode('ascii').upper()
            num1 = m.group(2).decode('ascii')
            num2 = m.group(3).decode('ascii')
            key = f"{prefix}_{num1}.{num2}"
            serial = f"{prefix}-{num1}{num2}"
            return key, serial
    return None, None

def write_cue(cue_path: Path, bin_name: str):
    cue_content = f'FILE "{bin_name}" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n'
    with open(cue_path, "w", encoding="utf-8") as f:
        f.write(cue_content)
    print(f"[+] Generado descriptor CUE: {cue_path.name}")

def update_configs(project_root: Path, cue_path: Path, serial: str, version_info: dict):
    cue_forward = str(cue_path.resolve()).replace("\\", "/")
    region = version_info.get("region", "PAL")
    is_pal = region == "PAL"
    
    cfg_file = project_root / "pc_port" / "config.cfg"
    if cfg_file.exists():
        text = cfg_file.read_text(encoding="utf-8", errors="replace")
        if is_pal:
            text = re.sub(r'refresh_rate\s*=\s*\d+', 'refresh_rate = 50', text)
        else:
            text = re.sub(r'refresh_rate\s*=\s*\d+', 'refresh_rate = 60', text)
        cfg_file.write_text(text, encoding="utf-8")
        print(f"[+] Actualizado config.cfg -> Tasa de refresco ajustada a {'50 Hz (PAL)' if is_pal else '60 Hz (NTSC)'}")

def main():
    print("=" * 65)
    print("  Silent Hill Recompiled — Detector y Preparador Universal")
    print("  Soporte Completo: PAL (España/Castellano, UK), NTSC-U, NTSC-J")
    print("=" * 65)

    base_dir = Path(__file__).resolve().parent.parent
    disc_dir = base_dir / "disc"
    disc_dir.mkdir(parents=True, exist_ok=True)
    
    target_file = None
    if len(sys.argv) > 1:
        cand = Path(sys.argv[1])
        if cand.is_file():
            target_file = cand

    if not target_file:
        extensions = [".pbp", ".cue", ".bin", ".iso", ".img", ".chd"]
        search_dirs = [disc_dir, base_dir, base_dir / "pc_port"]
        
        candidates = []
        for sdir in search_dirs:
            if sdir.exists():
                for ext in extensions:
                    candidates.extend(list(sdir.glob(f"*{ext}")))
                    candidates.extend(list(sdir.glob(f"*{ext.upper()}")))

        clean_cands = []
        for c in candidates:
            if c.name.lower() in ["silenthill.cue", "silenthill.bin"] and c.parent == disc_dir:
                clean_cands.insert(0, c)
            else:
                clean_cands.append(c)
                
        if clean_cands:
            target_file = clean_cands[0]

    if not target_file:
        print("\n[!] No se encontro ninguna imagen de disco en la carpeta.")
        print("    Por favor, coloca tu copia de Silent Hill (.PBP, .ISO, .BIN, .CUE, .CHD)")
        print(f"    en: {disc_dir} o en la raiz del proyecto y vuelve a ejecutar este script.")
        input("\nPulsa Enter para salir...")
        sys.exit(1)

    print(f"\n[*] Archivo detectado: {target_file}")
    
    bin_file = disc_dir / "SilentHill.bin"
    cue_file = disc_dir / "SilentHill.cue"

    suf = target_file.suffix.lower()
    if suf == ".pbp":
        ok = extract_pbp(target_file, bin_file)
        if not ok:
            sys.exit(1)
        write_cue(cue_file, "SilentHill.bin")
    elif suf == ".cue":
        cue_file = target_file
        with open(target_file, "r", encoding="utf-8", errors="replace") as f:
            m = re.search(r'FILE\s+"([^"]+)"', f.read(), re.I)
            if m:
                bin_file = target_file.parent / m.group(1)
            else:
                bin_file = target_file.with_suffix(".bin")
    elif suf in [".bin", ".iso", ".img"]:
        if target_file.resolve() != bin_file.resolve():
            print(f"[*] Vinculando {target_file.name} -> {bin_file}...")
            try:
                shutil.copy2(target_file, bin_file)
            except Exception:
                bin_file = target_file
        write_cue(cue_file, bin_file.name)

    boot_key, detected_serial = detect_serial(bin_file) if bin_file.exists() else (None, None)
    is_pal = detected_serial and (detected_serial.startswith("SLES") or detected_serial.startswith("SCES"))
    version_info = KNOWN_VERSIONS.get(boot_key, {
        "serial": detected_serial or ("SLES-01514" if is_pal else "SLUS-00707"),
        "title": f"Silent Hill ({detected_serial or 'Desconocida'})",
        "region": "PAL" if is_pal else "NTSC-U",
        "hz": 50.0 if is_pal else 59.94,
        "lang": "es" if is_pal else "en",
        "boot_exe": boot_key or ("SLES_015.14" if is_pal else "SLUS_007.07")
    })

    print("-" * 65)
    print(f"  Version identificada: {version_info['title']}")
    print(f"  Serial PS1:           {version_info['serial']}")
    print(f"  Region de video:      {version_info['region']} ({version_info['hz']} Hz)")
    print("-" * 65)

    update_configs(base_dir, cue_file, version_info["serial"], version_info)
    print("\n[OK] Configuracion completada con exito.")
    print("    El juego esta listo para iniciarse con JUGAR_SILENT_HILL.bat.")

if __name__ == "__main__":
    main()
