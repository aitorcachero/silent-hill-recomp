// Silent Hill Modern Remaster Shader
// (FidelityFX Texture Smoothing + Atmospheric Fog Neutralization + ACES Filmic)
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

    // 1. Multi-tap texture sampling
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

    // 2. Intelligent Ground Texel Smoothing (removes chunky blocky checkerboard patches)
    // On flat/subtle textures (asphalt road, mist), blend slightly with neighbors.
    // On high contrast edges (Harry, fences, snow, monsters), keep 100% razor sharp!
    vec3 crossAvg = 0.2 * (c + n + s + w + e);
    float smoothBlend = clamp(1.0 - contrast * 18.0, 0.0, 0.75);
    c = mix(c, crossAvg, smoothBlend);

    // 3. PS1 Lilac/Magenta Fog & Ground Chroma Neutralization
    // In original PS1 Silent Hill, the fog has an intense lilac/magenta tint (R > G, B >> G).
    // When modulated onto asphalt textures, it creates ugly magenta blotches.
    // We detect the purple/magenta excess and re-balance it to clean, cold atmospheric mist.
    float magentaExcess = max(0.0, min(c.r - c.g, c.b - c.g));
    float violetExcess  = max(0.0, c.b - max(c.r, c.g));

    float maxColor = max(c.r, max(c.g, c.b));
    float minColor = min(c.r, min(c.g, c.b));
    float saturation = (maxColor > 0.001) ? (maxColor - minColor) / maxColor : 0.0;

    // Only neutralize on low-to-medium saturation environmental areas (asphalt, fog)
    // Preserves rich vibrant colors (Harry's leather jacket, health drinks, blood, fire)
    float neutFactor = smoothstep(0.55, 0.08, saturation);
    c.r -= magentaExcess * 0.95 * neutFactor;
    c.b -= (magentaExcess * 0.90 + violetExcess * 0.40) * neutFactor;
    c.g += magentaExcess * 0.20 * neutFactor;

    // 4. ACES Filmic Tone Curve (balanced contrast rolloff without crushing)
    c = ACESFilm(c * 1.04);

    // 5. Subtle 35mm Film Grain (Removes 8-bit color banding, adds filmic texture)
    float grain = (hash(uv * vec2(texSize)) - 0.5) * 0.015;
    c = clamp(c + grain, 0.0, 1.0);

    // 6. Cinematic Vignette (Subtle edge focus)
    vec2 vigUV = uv * (1.0 - uv.yx);
    float vig = vigUV.x * vigUV.y * 15.0;
    vig = clamp(pow(vig, 0.10), 0.0, 1.0);
    c = mix(c * 0.92, c, vig);

    o = vec4(clamp(c, 0.0, 1.0), 1.0);
}
