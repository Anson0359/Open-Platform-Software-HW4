import sys
import configparser
import google.generativeai as genai

from flask import Flask, request, render_template, jsonify, json, abort
from linebot import (
    WebhookHandler,
    LineBotApi
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import(
    MessageEvent,
    TextMessage,
    FlexSendMessage,
    LocationSendMessage,
    VideoSendMessage,
    ImageSendMessage,
    StickerSendMessage
)

#Config Parser
config = configparser.ConfigParser()
config.read('config.ini')
genai.configure(api_key=config["Gemini"]["API_KEY"])

llm_role_description = """
你是一位大學教授，性格溫和沉穩，對待學生如對待孩子般親切
"""

# Use the model
#model = genai.GenerativeModel("gemini-1.5-flash-latest")
from google.generativeai.types import HarmCategory, HarmBlockThreshold
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT:HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH:HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT:HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT:HarmBlockThreshold.BLOCK_NONE,
    },
    generation_config={
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    },
    system_instruction=llm_role_description,
)
chat = model.start_chat(history=[])

app = Flask(__name__)

channel_access_token = config['Line']['CHANNEL_ACCESS_TOKEN']
channel_secret = config['Line']['CHANNEL_SECRET']
my_user_id = config['Line']['USER_ID']

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
if my_user_id is None:
    print('Specify USER_ID as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# 簡單記憶體資料庫：儲存使用者對話紀錄
user_input_history = {}  # key = user_id, value = list of strings

@app.route("/")
def home():
    try:
        gemini_result = gemini_llm_sdk('打個招呼')
        line_bot_api.push_message(my_user_id, TextMessage(text = gemini_result))
    except InvalidSignatureError:
        print('Invalid Signature Error, Please Check Your Channel Secret')
        abort(400)

    return "Line Bot Awake !"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent)
def message_text(event):
    messagetype = event.message.type
    if messagetype == 'text':
        message = event.message.text
        user_text = event.message.text
    else:
        message = messagetype
        user_text = messagetype
    
    user_id = event.source.user_id

    # 儲存歷史訊息
    if user_id not in user_input_history:
        user_input_history[user_id] = []
    user_input_history[user_id].append(user_text)

    # 傳送貼圖
    if message == 'Sticker' or message == 'sticker' or messagetype == 'sticker':
        output = StickerSendMessage(
            package_id = "11537",
            sticker_id = "52002744"
        )
    elif message == 'Image' or message == 'image' or messagetype == 'image':
        output = ImageSendMessage(
            original_content_url='https://p2.itc.cn/images01/20210413/6b32f7a29b6e4d8a81596779112efa59.jpeg',
            preview_image_url='https://p2.itc.cn/images01/20210413/6b32f7a29b6e4d8a81596779112efa59.jpeg'
        )
    elif message == 'Video' or message == 'video' or messagetype == 'video':
        output = VideoSendMessage(
            original_content_url='https://i.imgur.com/1BnZGQC.mp4',
            preview_image_url='https://i.imgur.com/wpM584d.jpg'
        )
    elif message == 'Location' or message == 'location' or messagetype == 'location':
        output = LocationSendMessage(
            title = 'Mask Map',
            address = '星巴克 內壢環中東門市',
            latitude = 24.964223577673593, 
            longitude = 121.25761669249557
        )
    elif message == 'Flex' or message == 'flex':
        output = FlexSendMessage(
            alt_text='Starbucks',
            contents={
                "type": "bubble",
                "hero": {
                    "type": "image",
                   "url": "https://developers-resource.landpress.line.me/fx/img/01_1_cafe.png",
                  "size": "full",
                  "aspectRatio": "20:13",
                  "aspectMode": "cover",
                  "action": {
                    "type": "uri",
                    "uri": "https://line.me/"
                  }
                },
                "body": {
                  "type": "box",
                  "layout": "vertical",
                  "contents": [
                    {
                      "type": "text",
                      "text": "星巴克",
                      "weight": "bold",
                      "size": "xl"
                    },
                    {
                      "type": "box",
                      "layout": "baseline",
                      "margin": "md",
                      "contents": [
                        {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                          },
                          {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                          },
                          {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                          },
                          {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                          },
                          {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://developers-resource.landpress.line.me/fx/img/review_gray_star_28.png"
                          },
                          {
                            "type": "text",
                            "text": "4.0",
                                "size": "sm",
                            "color": "#999999",
                            "margin": "md",
                            "flex": 0
                          }
                        ]
                      },
                      {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                          {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                              {
                                "type": "text",
                                "text": "Place",
                                "color": "#aaaaaa",
                                "size": "sm",
                                "flex": 1
                              },
                              {
                                "type": "text",
                                "wrap": True,
                                "color": "#666666",
                                "size": "sm",
                                "flex": 5,
                                "text": "桃園市中壢區環中東路168號"
                              }
                            ]
                          },
                          {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                              {
                                "type": "text",
                                "text": "Time",
                                "color": "#aaaaaa",
                                "size": "sm",
                                "flex": 1
                              },
                              {
                                "type": "text",
                                "text": "06:30 - 22:00",
                                "wrap": True,
                                "color": "#666666",
                                "size": "sm",
                                "flex": 5
                              }
                            ]
                          }
                        ]
                      }
                    ]
                  },
                  "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                      {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                          "type": "uri",
                          "label": "CALL",
                          "uri": "https://line.me/"
                        }
                      },
                      {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                          "type": "uri",
                          "label": "WEBSITE",
                          "uri": "https://www.google.com/maps/place/%E6%98%9F%E5%B7%B4%E5%85%8B+%E5%85%A7%E5%A3%A2%E7%92%B0%E4%B8%AD%E6%9D%B1%E9%96%80%E5%B8%82/@24.964228,121.2572625,17.12z/data=!4m6!3m5!1s0x346822069859a709:0xa6e5fb2cf627159!8m2!3d24.9641711!4d121.2576182!16s%2Fg%2F11b_1jwf8w?authuser=0&entry=ttu&g_ep=EgoyMDI1MDUxMy4xIKXMDSoASAFQAw%3D%3D"
                        }
                      },
                      {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [],
                        "margin": "sm"
                      }
                    ],
                    "flex": 0
                  }
                }
        )
    elif messagetype == 'text':
        gemini_result = gemini_llm_sdk(event.message.text)
        output = TextMessage(text=gemini_result)
    else:
        print(f'Undefined type : {messagetype}')
        gemini_result = gemini_llm_sdk(f'用中文，且用你的性格表達:我不接受{messagetype}訊息')
        output = TextMessage(text = gemini_result)

    line_bot_api.reply_message(
        event.reply_token, output
    )

@app.route("/history/<user_id>", methods=['GET'])
def get_history(user_id):
    history = user_input_history.get(user_id, [])
    return jsonify({
        "user_id": user_id,
        "history": history
    })

@app.route("/history/<user_id>", methods=['DELETE'])
def delete_history(user_id):
    if user_id in user_input_history:
        del user_input_history[user_id]
        chat.history.clear()
        return jsonify({"message": f"已刪除 {user_id} 的歷史紀錄"})
    else:
        return jsonify({"message": f"{user_id} 無任何紀錄"}), 404
    
def gemini_llm_sdk(user_input):
    try:
        #response = model.generate_content(user_input)
        response = chat.send_message(user_input)
        print(f"Question: {user_input}")
        print(f"Answer: {response.text}")
        return response.text
    except Exception as e:
        print(e)
        return "皆麽奈夫人故障中。"

if __name__ == '__main__':
    app.run()