import streamlit as st
from openai import OpenAI

openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

st.set_page_config(page_title="Drama Storyboard Generator")

st.title("Drama Storyboard Generator")

# 세션 상태 초기화
if 'storyboard_text' not in st.session_state:
    st.session_state.storyboard_text = ""

# 사용자 입력
drama_title = st.text_input("Enter the drama title:", value="나는 공주님")
episode_number = st.number_input("Enter the episode number:", min_value=1, value=1)
scene_description = st.text_area("Enter the scene description:", value="한 여자가 두 남자를 만나 사랑에 빠지는 이야기")

if st.button("Generate Storyboard"):
    # 스트리밍 출력을 위한 빈 컨테이너 생성
    streaming_container = st.empty()
    
    with st.spinner("Generating storyboard..."):
        # ChatGPT를 사용하여 스토리보드 텍스트 생성
        prompt = f"""As an experienced Korean drama screenwriter and storyboard artist, create a detailed storyboard for the following scene:

Title: {drama_title}
Episode: {episode_number}
Scene Description: {scene_description}

Please write the storyboard in Korean, following this structure:

1. 장면 설명: Provide a vivid, detailed description of the scene, including the setting, atmosphere, and character positions.

2. 대사: Write realistic, emotionally charged dialogue for the characters. Include character names and any significant pauses or actions between lines.

3. 카메라 앵글: Describe specific camera shots and movements that would best capture the emotion and action of the scene. Use technical terms where appropriate.

4. 조명: Detail the lighting setup, including the quality, direction, and color of light to enhance the mood of the scene.

5. 음향: Describe the background music, sound effects, and any significant ambient sounds that contribute to the scene's atmosphere.

6. 연기 지시: Provide clear instructions for the actors, including their emotional states, physical actions, and any subtle nuances in their performances.

7. 특수 효과: If applicable, describe any visual effects or practical effects needed for the scene.

Make the storyboard detailed, emotive, and cinematic, as if it were for a high-budget, critically acclaimed Korean drama series. Use vivid language and specific details to bring the scene to life. Ensure that the storyboard is written in Korean and return the storyboard in markdown. Ensure return only the storyboard, not any other text.
"""
        
        st.session_state.storyboard_text = ""
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                st.session_state.storyboard_text += chunk.choices[0].delta.content
                streaming_container.markdown(st.session_state.storyboard_text)

# 생성된 스토리보드 텍스트 표시
if st.session_state.storyboard_text:
    st.subheader("Generated Storyboard")
    st.text_area("Storyboard Content", value=st.session_state.storyboard_text, height=400)
    
    # 텍스트 파일로 다운로드 버튼 생성
    st.download_button(
        label="Download Storyboard Text",
        data=st.session_state.storyboard_text,
        file_name=f"{drama_title}_episode_{episode_number}_storyboard.txt",
        mime="text/plain"
    )
