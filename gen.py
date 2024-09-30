from flask import Flask, request, send_file
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from io import BytesIO

app = Flask(__name__)

base_model_path = "models/ponyDiffusionV6XL_v6StartWithThisOne.safetensors"
lora_path = "models/arcane_pony_v1-2_mx.safetensors"

pipe = StableDiffusionXLPipeline.from_single_file(base_model_path, torch_dtype=torch.float16)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe.load_lora_weights(lora_path)
pipe.to("cuda")

@app.route('/generate_image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt')
    negative_prompt = data.get('negative_prompt', "score_6_up, score_5_up, score_4_up, blurry, grayscale, text, simple background")
    width = data.get('width', 768)
    height = data.get('height', 1024)
    num_inference_steps = data.get('num_inference_steps', 20)
    guidance_scale = data.get('guidance_scale', 5)
    lora_scale = data.get('lora_scale', 0.95)

    prompt = f"score_9, score_8_up, score_8, {prompt}, volumetric lighting"

    image = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        cross_attention_kwargs={"scale": lora_scale},
    ).images[0]

    img_io = BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8188)
