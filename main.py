import streamlit as st
import json
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO
import anthropic

IMAGE_GENERATION_URL = st.secrets["IMAGE_GENERATION_URL"]
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

st.set_page_config(page_title="Arcane Storyboard Generator")

st.title("Arcane Storyboard Generator")
print('test')


def generate_and_save_image(prompt, output_path, **kwargs):
    payload = {
        "prompt": prompt,
        "negative_prompt": kwargs.get("negative_prompt", "score_6_up, score_5_up, score_4_up, blurry, grayscale, text, simple background"),
        "width": kwargs.get("width", 768),
        "height": kwargs.get("height", 1024),
        "num_inference_steps": kwargs.get("num_inference_steps", 20),
        "guidance_scale": kwargs.get("guidance_scale", 7.5),
        "lora_scale": kwargs.get("lora_scale", 0.95)
    }

    response = requests.post(IMAGE_GENERATION_URL, json=payload)
    
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image.save(output_path)
        print(f"이미지가 성공적으로 저장되었습니다: {output_path}")
    else:
        print(f"이미지 생성 실패. 상태 코드: {response.status_code}")
        print(f"오류 메시지: {response.text}")


# 세션 상태 초기화
if 'storyboard_text' not in st.session_state:
    st.session_state.storyboard_text = ""
if 'storyboard_images' not in st.session_state:
    st.session_state.storyboard_images = []
if 'storyboard_descriptions' not in st.session_state:
    st.session_state.storyboard_descriptions = []

# 사용자 입력
episode_title = st.text_input("Enter the episode title:", value="Arcane - Season 2")
scene_description = st.text_area("Enter the scene description:", value="징크스의 새로운 발명품이 예상치 못한 재앙을 일으키고, 바이, 케이틀린, 멜이 이를 해결하려 노력한다.\nJinx's new invention causes an unexpected catastrophe, and Vi, Caitlyn, and Mel strive to resolve the crisis.")


if st.button("Generate Storyboard"):
    date = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 새로운 생성 시 기존 데이터 초기화
    st.session_state.storyboard_text = ""
    st.session_state.storyboard_images = []
    st.session_state.storyboard_descriptions = []

    with st.spinner("Generating storyboard..."):
        prompt = f"""Create a new story arc for League of Legends Arcane animation, focusing on the characters Jinx(징크스), Vi(바이), Mel(멜), and Caitlyn(케이틀린). The story should follow this general direction: {scene_description}
Develop at least 4 distinct scenes based on this direction, each with a clear narrative purpose. The plot should explore themes of redemption, sisterhood, and the consequences of power.
Ensure each scene has a clear conflict, character development, and advances the overall plot. The story should have a clear beginning, development, climax, and resolution, with a distinct message or theme. Make the story compelling and interesting to the audience.
For each scene, provide:

A detailed description of the events in Korean and English.
An English prompt for image generation, including character descriptions and scene details.

Use the following character descriptions in the image prompts:

- jinx: jinx, a woman with blue hair and a black top, long hair, bangs
- vi: vi, orphan, a woman with red hair, short hair, bangs, grey eyes, red jacket, freckles
- caitlyn: caitlyn, a woman in a uniform, long hair, black hair, hat, gloves, police uniform, policewoman
- mel: mel, jewelry, earrings, dark skin

Include additional details about their actions and the background in the image prompts, separated by commas.
Return the results in a JSON format that can be parsed as a list of dictionaries in Python, with keys 'text' for the Korean and English description and 'prompt' for the English image generation prompt. Ensure return only the JSON string, not any other text or comments."""

        messages = [{
            "role": "user",
            "content": [{
                "type": "text",
                "text": prompt
            }]
        }]

        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=5000,
            temperature=0.9,
            system=prompt,
            messages=messages,
        )

        result = message.content[0].text

        st.subheader("JSON Response")
        st.json(result, expanded=False)

        json_result = json.loads(result)

    for i, item in enumerate(json_result):
        st.session_state.storyboard_text += f"{item['text']}\n\n"

        with st.spinner(f"Generating an image for scene #{i+1}..."):
            image_path = f"result/{date}_{i}.png"
            generate_and_save_image(item['prompt'], image_path)

            st.session_state.storyboard_images.append(image_path)
            st.session_state.storyboard_descriptions.append(item['text'])

            col1, col2 = st.columns(2)
            with col1:
                st.image(image_path)
            with col2:
                st.write(item['text'])

    with open(f"result/{date}_storyboard.txt", "w", encoding="utf-8") as file:
        file.write(st.session_state.storyboard_text)

    st.rerun()


if st.session_state.storyboard_images:
    st.subheader("Generated Storyboard")

    for i, (img_path, description) in enumerate(zip(st.session_state.storyboard_images, st.session_state.storyboard_descriptions)):
        col1, col2 = st.columns(2)
        with col1:
            st.image(img_path)
        with col2:
            st.write(description)


if st.session_state.storyboard_text:
    st.subheader("Generated Text")

    st.text_area("Storyboard Content", value=f"# {episode_title}\n\n{st.session_state.storyboard_text}", height=400)

    st.download_button(
        label="Export Storyboard Text",
        data=st.session_state.storyboard_text,
        file_name=f"{episode_title}_storyboard.txt",
        mime="text/plain"
    )
