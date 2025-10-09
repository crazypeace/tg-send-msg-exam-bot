import logging
import random
import os
import importlib
import yaml
import re
from pathlib import Path
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# Bot Token - 从 BotFather 获取
BOT_TOKEN = "BOT_TOKENBOT_TOKENBOT_TOKEN"

# 仓库频道 ID
STORAGE_CHANNEL_ID = None   # 如果不需要暂存消息就设为 None

# 格式: -100xxxxxxxxxx 或者直接用 @channelname
# STORAGE_CHANNEL_ID = '-100' + '123456789'  # 请替换为你的仓库频道ID

# 群组默认权限
default_permissions = ChatPermissions(
    can_send_messages=True,
    can_send_photos=True,
    can_send_videos=True,
    can_send_video_notes=True,
    can_send_audios=True,
    can_send_voice_notes=True,
    can_send_documents=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
    can_send_polls=True,
)

# 日志目录和文件
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f'{Path(__file__).stem}_{datetime.now().strftime("%Y%m%d")}.log'

# 配置日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 文件处理器
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(formatter)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# 设置日志器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# YAML 文件路径
VALID_USERS_FILE = Path(__file__).parent / 'valid.yaml'

# 存储待验证的用户信息
# pending_users[user.id] = {
#     'chat_id': chat.id,
#     'join_time': datetime.now(),
#     'chat_title': chat.title,
#     'answer': correct_answer,
#     'question': question,
#     'stored_messages': [message_ids]  # 存储在仓库频道的消息ID列表
# }
pending_users = {}

# 验证用户列表缓存
valid_users_cache = {}

def load_valid_users():
    """从 YAML 文件加载已验证用户"""
    global valid_users_cache
    
    if not VALID_USERS_FILE.exists():
        valid_users_cache = {}
        return valid_users_cache
    
    try:
        with open(VALID_USERS_FILE, 'r', encoding='utf-8') as f:
            valid_users_cache  = yaml.safe_load(f) or {}
        logger.info(f"已加载 {len(valid_users_cache)} 个已验证用户")
    except Exception as e:
        logger.error(f"加载 valid.yaml 失败: {e}")
        valid_users_cache = {}
    
    return valid_users_cache


def save_valid_users(valid_users):
    """保存已验证用户到 YAML 文件"""
    try:
        with open(VALID_USERS_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(valid_users_cache, f, allow_unicode=True, sort_keys=False)
        logger.info(f"已保存 {len(valid_users_cache)} 个已验证用户到 valid.yaml")
    except Exception as e:
        logger.error(f"保存 valid.yaml 失败: {e}")


def add_valid_user(user_id, username, full_name):
    """添加已验证用户"""
    valid_users_cache[user_id] = {
        'username': username,
        'full_name': full_name,
        'verified_at': datetime.now().isoformat()
    }
    save_valid_users()
    logger.info(f"用户 {user_id} ({full_name}) 已添加到已验证列表")


def is_valid_user(user_id):
    """检查用户是否已验证"""
    return user_id in valid_users_cache


def get_random_module():
    # 找出 pset 目录下的所有 .py 文件（排除 __init__.py）
    files = [
        f[:-3] for f in os.listdir("pset")
        if f.endswith(".py") and f != "__init__.py"
    ]
    # 随机选择一个
    chosen = random.choice(files)
    # 动态导入
    module = importlib.import_module(f"pset.{chosen}")
    return module


async def delete_message(context: ContextTypes.DEFAULT_TYPE):
    """删除消息的回调函数"""
    job_data = context.job.data
    try:
        await context.bot.delete_message(
            chat_id=job_data['chat_id'],
            message_id=job_data['message_id']
        )
    except Exception as e:
        logger.error(f"删除消息失败: {e}")


async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理群组消息，检查发送者是否已验证"""
    user = update.effective_user
    message = update.message
    chat = update.effective_chat
    
    # 跳过机器人自己, 也跳过其它被管理员加进群的机器人
    if user.is_bot:
        return
    
    # 检查是否已验证
    if is_valid_user(user.id):
        # 已验证用户，允许消息通过
        return
    
    logger.info(f"检测到未验证用户 {user.id} ({user.full_name}) 在群组 {chat.id} 发送消息")
    
    try:
        # 1. 禁言该用户
        await context.bot.restrict_chat_member(
            chat_id=chat.id,
            user_id=user.id,
            permissions=ChatPermissions(
                can_send_messages=False
            )
        )
        logger.info(f"已禁言用户 {user.id}")
        
        # 2. 转发消息到仓库频道
        stored_msg = None
        if STORAGE_CHANNEL_ID:
          logger.info(f'STORAGE_CHANNEL_ID: {STORAGE_CHANNEL_ID}')
          stored_msg = await message.forward(chat_id=STORAGE_CHANNEL_ID)
          logger.info(f"消息已转发到仓库频道，消息ID: {stored_msg.message_id}")
        
        # 3. 删除群组中的原消息
        await message.delete()
        logger.info(f"已删除群组中的消息")
        
        # 4. 检查用户是否已经在待验证列表中
        if user.id not in pending_users:
            # 生成验证问题
            mod = get_random_module()
            question, correct_answer = mod.buildQA()
            
            pending_users[user.id] = {
                'chat_id': chat.id,
                'join_time': datetime.now(),
                'chat_title': chat.title,
                'answer': correct_answer,
                'question': question,
                'stored_messages': []
            }
            logger.info(f"已为用户: {user.id} 生成验证问题: {question} 正确答案: {correct_answer}")
        
        # 5. 将存储的消息ID添加到列表
        if STORAGE_CHANNEL_ID and stored_msg:
          pending_users[user.id]['stored_messages'].append({
              'message_id': stored_msg.message_id,
              'original_chat_id': chat.id
          })
          logger.info(f"已为用户: {user.id} 暂存消息: {stored_msg.message_id}")
        
        # 6. 在群组中发送提醒消息
        warning_msg = await context.bot.send_message(
            chat_id=chat.id,
            text=(
                f'⚠️ {user.mention_markdown()} 你未完成验证\n'
                f'🔒 已暂时禁言\n'
                f'💬 请私聊机器人 [@{context.bot.username}](https://t.me/{context.bot.username}) 并发送 /start 完成验证'
            ),
            parse_mode='Markdown'
        )
        
        # 120秒后删除提醒消息
        context.job_queue.run_once(
            delete_message,
            120,
            data={'chat_id': chat.id, 'message_id': warning_msg.message_id}
        )
        
    except Exception as e:
        logger.error(f"处理未验证用户消息时出错: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    user = update.effective_user
    user_id = user.id
    
    # 检查是否是待验证用户
    if user_id in pending_users:
        user_info = pending_users[user_id]
        
        await update.message.reply_text(
            f'👋 欢迎！你正在验证 *{user_info["chat_title"]}* 中的发言权限\n\n'
            f'❓ 请问：*{user_info["question"]}*\n\n'
            f'请直接输入答案',
            parse_mode='Markdown'
        )
        
        logger.info(f"用户 {user_id} 开始验证流程")
    else:
        await update.message.reply_text(
            "👋 你好！我是群组验证机器人。\n\n"
            "🔹 当你在群组中发送消息时，我会检查你是否已验证\n"
            "🔹 未验证用户会被暂时禁言，并需要完成人机验证\n"
            "🔹 未验证用户需要向我发送 /start 并回答验证问题\n"
            "🔹 验证通过后，我会自动解除禁言"
        )


async def handle_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理用户的验证答案"""
    user = update.effective_user
    user_id = user.id
    message_text = update.message.text.strip()
    
    # 检查是否是待验证用户
    if user_id not in pending_users:
        return
    
    user_info = pending_users[user_id]
    user_answer = message_text.strip()
    correct_answer = user_info['answer']

    # 统一为小写, 去掉空白字符
    correct_answer = re.sub(r'\s+', '', correct_answer.lower())
    user_answer = re.sub(r'\s+', '', user_answer.lower())
    if correct_answer in user_answer:
        # 答案正确
        chat_id = user_info['chat_id']
        
        try:
            # 1. 解除禁言
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=default_permissions
            )
            logger.info(f"已解除用户 {user_id} 的禁言")
            
            # 2. 添加到已验证用户列表
            add_valid_user(
                user_id=user_id,
                username=user.username or "无用户名",
                full_name=user.full_name
            )
            
            # 3. 从仓库频道转发消息回群组
            restored_count = 0
            if STORAGE_CHANNEL_ID:
              stored_messages = user_info.get('stored_messages', [])
              
              for msg_info in stored_messages:
                  try:
                      await context.bot.forward_message(
                          chat_id=msg_info['original_chat_id'],
                          from_chat_id=STORAGE_CHANNEL_ID,
                          message_id=msg_info['message_id']
                      )
                      restored_count += 1
                  except Exception as e:
                      logger.error(f"转发消息 {msg_info['message_id']} 失败: {e}")
              
              logger.info(f"已将 {restored_count} 条消息转发回群组")
            
            # 4. 删除待验证记录
            del pending_users[user_id]
            
            # 5. 计算验证时间
            time_taken = (datetime.now() - user_info['join_time']).seconds
            
            await update.message.reply_text(
                f"✅ 验证成功！\n\n"
                f"用时：{time_taken}秒\n"
                f"你现在可以在 *{user_info['chat_title']}* 中发言了。",
                parse_mode='Markdown'
            )
            
            # 6. 在群组中通知
            msg = await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"✅ {user.mention_markdown()} 已通过验证\n"
                    f"⏱ 用时 {time_taken}秒"
                ),
                parse_mode='Markdown'
            )
            
            # 10秒后删除通知消息
            context.job_queue.run_once(
                delete_message,
                10,
                data={'chat_id': chat_id, 'message_id': msg.message_id}
            )
            
            logger.info(f"用户 {user_id} 验证成功，用时 {time_taken}秒")
            
        except Exception as e:
            logger.error(f"解除禁言时出错: {e}")
            await update.message.reply_text(f"❌ 验证出错: {e}")
    else:
        # 答案错误
        await update.message.reply_text(
            f"❌ 答案错误，请重试！\n\n"
            f"问题：*{user_info['question']}*",
            parse_mode='Markdown'
        )
        logger.info(f"用户 {user_id} 答案错误: {user_answer} (正确答案: {correct_answer})")


def main():
    """启动机器人"""
    
    # 加载验证用户列表缓存
    load_valid_users()
    
    # 创建应用
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 添加处理器
    application.add_handler(CommandHandler("start", start))
    
    # 处理群组消息（检查验证状态）
    application.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & ~filters.COMMAND & ~filters.StatusUpdate.ALL,
            handle_group_message
        )
    )
    
    # 处理私聊消息（验证答案）
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND,
            handle_verification
        )
    )
    
    # 启动机器人
    logger.info("机器人启动中...")
    logger.info(f"仓库频道ID: {STORAGE_CHANNEL_ID}")
    logger.info(f"已验证用户文件: {VALID_USERS_FILE}")
    
    application.run_polling(allowed_updates=["message"])

if __name__ == '__main__':
    main()
