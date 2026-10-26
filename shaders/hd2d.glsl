// Silent Hill Modern Remaster Shader (FidelityFX CAS + ACES Filmic + Atmospheric Fog)
// Designed for 4K UHD rendering on modern GPUs (RTX 5060+)

vec3 sampleColor(vec2 uv) {
    return texture(u_tex, clamp(uv, vec2(0.0), vec2(1.0))).rgb;
}

// ACES Filmic Tone Mapping (Photorealistic highlight rolloff & deep shadow recovery)
vec3 ACESFilm(vec3 x) {
    float a = 2.51;
    float b = 0.03;
    float c = 2.43;
    float d = 0.59;
    float e = 0.14;
    return clamp((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0);
}

// Subtle pseudo-random hash for fine 35mm photographic micro-grain
float hash(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

void main() {
    vec2 uv = v_uv;
    ivec2 texSize = textureSize(u_tex, 0);
    vec2 px = 1.0 / vec2(texSize);

    // 1. FidelityFX Contrast-Adaptive Sharpening (CAS)
    // Sharpens texture micro-details (leather, bricks, rust, road grit)
    // without creating edge ringing or artifacts.
    vec3 c = sampleColor(uv);
    vec3 n = sampleColor(uv + vec2(0.0, -px.y));
    vec3 s = sampleColor(uv + vec2(0.0,  px.y));
    vec3 w = sampleColor(uv + vec2(-px.x, 0.0));
    vec3 e = sampleColor(uv + vec2( px.x, 0.0));

    // Calculate local luminance contrast
    float lumaC = dot(c, vec3(0.2126, 0.7152, 0.0722));
    float lumaN = dot(n, vec3(0.2126, 0.7152, 0.0722));
    float lumaS = dot(s, vec3(0.2126, 0.7152, 0.0722));
    float lumaW = dot(w, vec3(0.2126, 0.7152, 0.0722));
    float lumaE = dot(e, vec3(0.2126, 0.7152, 0.0722));

    float minLuma = min(lumaC, min(min(lumaN, lumaS), min(lumaW, lumaE)));
    float maxLuma = max(lumaC, max(max(lumaN, lumaS), max(lumaW, lumaE)));
    float contrast = maxLuma - minLuma;

    // Adaptive sharpening weight (stronger on subtle textures, relaxed on high-contrast edges)
    float sharpWeight = clamp(0.18 * (1.0 - contrast), 0.0, 0.15);
    vec3 sharpColor = c + (c - 0.25 * (n + s + w + e)) * sharpWeight;
    c = clamp(sharpColor, 0.0, 1.0);

    // 2. ACES Filmic Tone Curve & Modern Color Grading
    // Gives cinematic depth to flashlight and fog
    c = ACESFilm(c * 1.08);

    // 3. Cinematic Atmospheric Horror Palette (Preserve eerie grime & rust)
    float finalLuma = dot(c, vec3(0.2126, 0.7152, 0.0722));
    c = mix(vec3(finalLuma), c, 1.06);

    // 4. Subtle 35mm Film Grain (Removes 8-bit fog color banding, adds filmic texture)
    float grain = (hash(uv * vec2(texSize)) - 0.5) * 0.022;
    c = clamp(c + grain, 0.0, 1.0);

    // 5. Cinematic Vignette (Focus on the flashlight cone and center view)
    vec2 vigUV = uv * (1.0 - uv.yx);
    float vig = vigUV.x * vigUV.y * 15.0;
    vig = clamp(pow(vig, 0.12), 0.0, 1.0);
    c = mix(c * 0.88, c, vig);

    o = vec4(clamp(c, 0.0, 1.0), 1.0);
}
