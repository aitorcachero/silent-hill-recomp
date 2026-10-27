#!/usr/bin/env python3
"""
Silent Hill Recompiled — Detector y Preparador Universal de Disco
Soporte completo:
  - PAL España (SLES-01514 en castellano)
  - PAL Europa (SCES-01514 inglés)
  - NTSC-U USA / Doblaje al Castellano (SLUS-00707 v1.0 / v1.1)
  - NTSC-J Japón (SLPM-86192 original / Konami The Best SLPM-86641 / PSone Books SLPM-87328)
Formatos: .PBP, .BIN/.CUE, .ISO, .IMG, .CHD
"""

import os
import sys
import struct
import zlib
import re
import shutil
import subprocess
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
        "title": "Silent Hill (USA / Doblaje Castellano)",
        "region": "NTSC-U",
        "hz": 59.94,
        "lang": "es",
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

def extract_exe_from_iso(bin_path: Path, out_path: Path, exe_name: str):
    if out_path.exists() and out_path.stat().st_size > 0:
        try:
            with open(out_path, "rb") as f_chk:
                chk_hdr = f_chk.read(2048 + 4)
            if chk_hdr[:8] == b"PS-X EXE" and len(chk_hdr) >= 2052 and chk_hdr[2048:2052] != b"\x8c\x49\x28\x85":
                return True
        except Exception:
            pass
    try:
        # Intentar con sectores de 2352 (RAW/BIN) y 2048 (ISO estandar)
        for sector_size in [2352, 2048]:
            try:
                with open(bin_path, "rb") as f:
                    header_candidates = [24, 16] if sector_size == 2352 else [0]
                    pvd = None
                    header_size = 0
                    for hs in header_candidates:
                        f.seek(16 * sector_size + hs)
                        block = f.read(2048)
                        if block[1:6] == b"CD001":
                            pvd = block
                            header_size = hs
                            break
                    if not pvd:
                        continue
                    root_rec = pvd[156:156+34]
                    root_lba = struct.unpack("<I", root_rec[2:6])[0]
                    root_len = struct.unpack("<I", root_rec[10:14])[0]
                    f.seek(root_lba * sector_size + header_size)
                    dir_data = f.read(root_len)
                    pos = 0
                    while pos < len(dir_data):
                        rec_len = dir_data[pos]
                        if rec_len == 0:
                            pos = (pos + 2048) & ~2047
                            continue
                        rec = dir_data[pos:pos+rec_len]
                        lba = struct.unpack("<I", rec[2:6])[0]
                        size = struct.unpack("<I", rec[10:14])[0]
                        name_len = rec[32]
                        name = rec[33:33+name_len].decode("latin1", "ignore")
                        if exe_name.lower() in name.lower():
                            f.seek(lba * sector_size)
                            out_bytes = bytearray()
                            remaining = size
                            while remaining > 0:
                                sec = f.read(sector_size)
                                take = min(remaining, 2048)
                                out_bytes.extend(sec[header_size:header_size+take])
                                remaining -= take
                            out_path.write_bytes(out_bytes)
                            print(f"[+] Extraido binario ejecutable de PS1: {out_path.name} ({len(out_bytes)} bytes)")
                            return True
                        pos += rec_len
            except Exception:
                continue
    except Exception as e:
        print(f"[!] Advertencia extrayendo ejecutable: {e}")
    return False

def update_configs(project_root: Path, cue_path: Path, serial: str, version_info: dict):
    cue_forward = str(cue_path.resolve()).replace("\\", "/")
    region = version_info.get("region", "PAL")
    is_pal = region == "PAL"
    
    # Marcador de region para el launcher
    disc_dir = project_root / "disc"
    tag_usa = disc_dir / "variant_usa.tag"
    tag_pal = disc_dir / "variant_pal.tag"
    if not is_pal:
        tag_usa.write_text("USA\n", encoding="utf-8")
        if tag_pal.exists(): tag_pal.unlink()
        print("[+] Marcador de variante activado: USA / Doblaje Castellano (SLUS-00707)")
    else:
        tag_pal.write_text("PAL\n", encoding="utf-8")
        if tag_usa.exists(): tag_usa.unlink()
        print("[+] Marcador de variante activado: PAL España / Europa (SLES-01514)")
    
    # Escribir disc.cfg
    for d in [project_root, project_root / "build-release"]:
        if d.exists():
            (d / "disc.cfg").write_text(cue_forward + "\n", encoding="utf-8")
            if not is_pal:
                (d / "disc" / "variant_usa.tag").parent.mkdir(parents=True, exist_ok=True)
                (d / "disc" / "variant_usa.tag").write_text("USA\n", encoding="utf-8")
            
    # Actualizar settings.toml
    for d in [project_root, project_root / "build-release"]:
        st = d / "settings.toml"
        if st.exists():
            txt = st.read_text(encoding="utf-8")
            txt = re.sub(r'path\s*=\s*"[^"]*"', f'path = "{cue_forward}"', txt)
            st.write_text(txt, encoding="utf-8")

def main():
    print("=" * 65)
    print("  Silent Hill Recompiled — Detector y Preparador Universal")
    print("  Soporte Completo: PAL (España/Castellano, UK), NTSC-U / Doblaje")
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
        extensions = [".chd", ".pbp", ".cue", ".bin", ".iso", ".img"]
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
        print("    Por favor, coloca tu copia de Silent Hill (.CHD, .PBP, .ISO, .BIN, .CUE)")
        print(f"    en: {disc_dir} o en la raiz del proyecto y vuelve a ejecutar este script.")
        input("\nPulsa Enter para salir...")
        sys.exit(1)

    print(f"\n[*] Archivo detectado: {target_file}")
    
    bin_file = disc_dir / "SilentHill.bin"
    cue_file = disc_dir / "SilentHill.cue"

    suf = target_file.suffix.lower()
    if suf == ".chd":
        print(f"[*] Descomprimiendo imagen CHD: {target_file.name}...")
        chdman = None
        for cand_chdman in [base_dir / "tools" / "chdman.exe", base_dir.parent / "tools" / "chdman.exe"]:
            if cand_chdman.exists():
                chdman = cand_chdman
                break
        if chdman:
            cmd = [str(chdman), "extractcd", "-i", str(target_file), "-o", str(cue_file), "-ob", str(bin_file)]
            subprocess.run(cmd, check=True)
            print(f"[+] CHD extraido exitosamente a: {bin_file.name}")
        else:
            print("[!] Error: No se encontro chdman.exe para descomprimir el CHD.")
            sys.exit(1)
    elif suf == ".pbp":
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

    # Extraer el binario ejecutable de arranque si es necesario
    extract_exe_from_iso(bin_file, disc_dir / version_info["boot_exe"], version_info["boot_exe"])

    update_configs(base_dir, cue_file, version_info["serial"], version_info)
    print("\n[OK] Configuracion completada con exito.")
    print("    El juego esta listo para iniciarse con JUGAR_SILENT_HILL.bat o SilentHill.exe.")

if __name__ == "__main__":
    main()
