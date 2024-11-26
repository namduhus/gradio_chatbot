# import 하기
import requests
import gradio as gr


##################


## 이전 내용 기록
def get_history_message(histories):
    history_list = list()
    
    history_length = 5
    history_index = 0
    
    for history in histories:

        if history_index >= history_length:
            break
        
        message1 = history[0]
        message2 = history[1]
        
        history_list.append({
            "role": 'assistant',
            "content": message1
        })
        history_list.append({
            "role": "assistant",
            "content": message2
        })
        
        history_index += 1
    return history_list

##################

## request 및 API 설정 및 기본 설정
def request_gpt(prompt, history_list):
    
    # endpoint
    endpoint = "URL"    
    
    ai_search_endpoint = "URL" # azure search service URL
    ai_search_key = "Key" # Azure Search Key
    ai_search_index = "sportspot2" # Azure search index
    
    # method(post)
    headers = {
        "Content-Type" : "application/json",
        "api-key": "key" #코드 보기 에서 나온 key 복사
    }
    message_list = list()
    
    #system
    message_list.append({
        "role": "system",
        "content": "너는 이제부터 전국체육시설을 친절하게 말해주는 서비스직 에이스야. 앞으로 사용자가 질문을 하면 잘 대답해줘야해. 또한 사용자가 무슨 지역에 살고 무슨 스포츠를 하고싶어하는지 그리고 어떤 목적을 가지고 질문을 하면 잘 파악해서 자세하게 알려줘야해."
    })
    # 이전 메세지
    message_list.extend(history_list)
    # prompt
    message_list.append({
        "role": "user",
        "content": prompt
    })
    payload = {
        "messages": message_list,
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800,
        "data_sources": [
        {
            "type": "azure_search",
            "parameters": {
                "endpoint": ai_search_endpoint,
                "semantic_configuration": "sport-segmantic",
                "query_type": "semantic",
                "strictness": 3,
                "top_n_documents": 5,
                "key": ai_search_key,
                "indexName": ai_search_index
            }
        }
        ]
    }
    
    response = requests.post(endpoint, headers=headers, json=payload)
    
    if response.status_code == 200:
        response_json = response.json()
        content = response_json["choices"][0]["message"]["content"]
        return content
    else:
        return f"{response.status_code}, {response.text}"
      



def click_send(prompt, histories):
    history_list = get_history_message(histories=histories)
    response_text = request_gpt(prompt, history_list)
    histories.append((prompt, response_text))
    return histories, ""


with gr.Blocks(css="""
    .gradio-container {
        background-color: grey; /* 회색 배경 */
        font-family: 'Arial', sans-serif;
    }
    #chatbot-container {
        background-color: white; /* 흰색 배경 */
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); /* 그림자 추가 */
        max-width: 800px;
        margin: 50px auto;
    }
    #input-container {
        display: flex;
        justify-content: space-between;
        margin-top: 20px;
    }
    .gr-button {
        background-color: #1E90FF !important; /* 파란색 버튼 */
        color: white !important; /* 버튼 텍스트 색상 */
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-size: 1em !important;
        cursor: pointer !important;
    }
    .gr-button:hover {
        background-color: #0056b3 !important; /* 어두운 파란색 버튼 hover 효과 */
    }
    .chatbot-message.user {
        background-color: #87CEFA; /* 하늘색 사용자 메시지 */
        color: white;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .chatbot-message.assistant {
        background-color: #32CD32; /* 초록색 응답 메시지 */
        color: white;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
""") as demo:
    with gr.Column(elem_id="chatbot-container"):
        gr.Markdown("## 🏀 스포츠 도우미챗봇", elem_id="header")
        gr.Markdown("스포츠 일정, 장소 추천 및 운동 팁을 제공합니다.", elem_id="subheader")
        
        chatbot = gr.Chatbot(label="스포츠 채팅 내용",show_label=False)
        
        with gr.Row(elem_id="input-container"):
            input_textbox = gr.Textbox(
                lines=2,
                placeholder="궁금사항을 입력하세요 (예: 00지역 원하는 스포츠 체육시설 또는 강좌 프로그램).",
                show_label=False,
            )
            send_button = gr.Button("전송")
        
        input_textbox.submit(fn=click_send, inputs=[input_textbox, chatbot], outputs=[chatbot, input_textbox])
        send_button.click(fn=click_send, inputs=[input_textbox, chatbot], outputs=[chatbot, input_textbox])

    


# Gradio 실행
if __name__ == "__main__":
    demo.launch()