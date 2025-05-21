def build_prompt(product, tone="Professional"):
    tone_guidance = {
        "Professional": "Use a formal and informative tone.",
        "Casual": "Use a relaxed and friendly tone.",
        "Luxury": "Use elegant and aspirational language.",
        "Minimal": "Keep it concise and clean.",
        "Playful": "Add emojis and use a fun tone."
    }
    
    return f"""
You are an e-commerce copywriter.

Write a {tone.lower()}-styled product description (2–3 sentences) using this data:
- Product: {product['product_name']}
- Brand: {product['brand']}
- Material: {product['material']}
- Features: {product['features']}

{tone_guidance.get(tone, '')}
Make it SEO-friendly and engaging.
"""
