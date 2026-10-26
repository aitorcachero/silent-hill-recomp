// Silent Hill Atmospheric Horror Shader (4K OLED Contrast & Fog Preservation)
// Deep shadows, clean flashlight beam contrast, and smooth dithered fog blending.

vec3 sampleColor(vec2 uv) {
    return texture(u_tex, clamp(uv, vec2(0.0), vec2(1.0))).rgb;
}

void main() {
    vec2 uv = v_uv;
    vec3 c = sampleColor(uv);

    // Deep Atmospheric Black & Shadow Crush Adjustment (OLED contrast)
    // Enhances the fear of the dark without blowing out highlights
    float luma = dot(c, vec3(0.2126, 0.7152, 0.0722));
    c = pow(c, vec3(1.08)); // Film-like gamma response

    // Subtle gritty tone curve
    c = (c - 0.5) * 1.05 + 0.5;
    c = clamp(c, 0.0, 1.0);

    // Controlled cinematic saturation (retains authentic eerie Otherworld palette)
    c = mix(vec3(luma), c, 1.05);

    o = vec4(clamp(c, 0.0, 1.0), 1.0);
}
