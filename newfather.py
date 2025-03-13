import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup,LabeledPrice
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import asyncio
from datetime import datetime, timedelta
import asyncio
from telegram.ext import Application, CommandHandler, filters, CallbackQueryHandler, MessageHandler, PreCheckoutQueryHandler
import pymysql
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, PreCheckoutQueryHandler
from datetime import datetime
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, PreCheckoutQueryHandler
from datetime import datetime

import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import json

# Varsayılan kullanıcı verisi
user_data = {
    "memberships": {},
    "banned_users": []
}

# JSON dosyasını oluştur ve veriyi kaydet
with open("kullanici.json", "w") as file:
    json.dump(user_data, file, indent=4)

# Assume AUTHORIZED_USERS, user_memberships, and MEMBERSHIP_PLANS are already defined

async def add_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Bu komutu kullanma yetkiniz yok.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("Kullanım: /ekle <membership_type> <user_id>")
        return

    membership_type = context.args[0].lower()
    if membership_type == "sinirsiz":
        membership_type = "Unlimited"
    elif membership_type == "plus":
        membership_type = "Plus"
    elif membership_type == "vip":
        membership_type = "VIP"
    else:
        await update.message.reply_text("Geçersiz üyelik tipi. 'plus', 'vip' veya 'sinirsiz' kullanın.")
        return

    try:
        user_id = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Geçersiz kullanıcı ID'si.")
        return

    # Kullanıcı üyeliğini kaydetme
    user_memberships[user_id] = membership_type
    user_matches[user_id] = MEMBERSHIP_PLANS[membership_type]['matches']

    # Kullanıcı bilgilerini JSON dosyasına kaydet
    save_to_json()

    await update.message.reply_text(f"{user_id} ID'li kullanıcıya {membership_type} üyeliği verildi.")
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"Tebrikler! Size {membership_type} üyeliği verildi. Artık tüm özellikleri kullanabilirsiniz."
        )
    except Exception as e:
        logging.error(f"Error sending message to user {user_id}: {str(e)}")
        await update.message.reply_text(f"Kullanıcıya bilgilendirme mesajı gönderilemedi, ancak üyelik başarıyla eklendi.")

def save_to_json(filename="kullanici.json") -> None:
    data = {
        "memberships": user_memberships,
        "banned_users": list(banned_users)
    }
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
    print("JSON dosyasına veri başarıyla kaydedildi.")


def add_admin_handlers(application):
    application.add_handler(CommandHandler("ekle", add_membership))

# Add this to your main() function
# add_admin_handlers(application)
# Referans sistemi için global değişken
referrals = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id in banned_users:
        await update.message.reply_text("Üzgünüz, bu bottan yasaklandınız.")
        return

    all_users.add(user.id)
    if user.id not in user_matches:
        user_matches[user.id] = 999

    # Referral kontrolü
    if context.args and context.args[0].isdigit() and int(context.args[0]) != user.id:
        referrer_id = int(context.args[0])
        if referrer_id in referrals:
            referrals[referrer_id] += 1
        else:
            referrals[referrer_id] = 1
        await update.message.reply_text(f"Sizi davet eden kullanıcıya 1 referans puanı eklendi!")

    # ... (geri kalan start fonksiyonu aynı kalacak)

async def ref(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id in banned_users:
        await update.message.reply_text("Üzgünüz, bu bottan yasaklandınız.")
        return
    
    user_ref_link = f"https://t.me/{context.bot.username}?start={user.id}"
    user_referrals = referrals.get(user.id, 0)
    
    ref_message = f"""Referans Bilgileriniz:

Referans linkiniz: {user_ref_link}
Şu ana kadar {user_referrals} kişiyi yönlendirdiniz!

Bu linki paylaşarak arkadaşlarınızı davet edebilirsiniz.

Özel Teklif: 2 referans getirdiğinizde, kazandığınız Star'ların %5'unu bonus olarak alabilirsiniz!

Referans sayınız: {user_referrals}"""

    await update.message.reply_text(ref_message)    

async def myref(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id in banned_users:
        await update.message.reply_text("Üzgünüz, bu bottan yasaklandınız.")
        return
    
    user_referrals = referrals.get(user.id, 0)
    all_users.add(user.id)
    if user.id not in user_matches:
        user_matches[user.id] = 999

    # Referral kontrolü
    if context.args and context.args[0].isdigit() and int(context.args[0]) != user.id:
        referrer_id = int(context.args[0])
        if referrer_id in referrals:
            referrals[referrer_id] += 1
        else:
            referrals[referrer_id] = 1
        
        # 2 referans kontrolü
        if referrals[referrer_id] == 2:
            await context.bot.send_message(
                chat_id=referrer_id,
                text="Tebrikler! 2 referansa ulaştınız. %5 Star bonusunuzu almak için lütfen @anonimsohbetbotudestek ile iletişime geçin."
            )
    myref_message = f"""Referans İstatistikleriniz:

Toplam yönlendirdiğiniz kişi sayısı: {user_referrals}

Her yönlendirme size ekstra eşleşme hakkı kazandırır!"""

    await update.message.reply_text(myref_message)
    await update.message.reply_text(f"Sizi davet eden kullanıcıya 1 referans puanı eklendi!")


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = '7608806197:AAGssF78kOHqmSlSgXdwUaCJN5V2Va6qFeU'
ADMIN_GROUP_ID = -1002095036242
AUTHORIZED_USERS = {6840212721,1214170912}

# Data structures
waiting_users = {'male': [], 'female': []}
matches = {}
referrals = {}
user_matches = {}
user_memberships = {}
user_genders = {}
all_users = set()
banned_users = set()

MEMBERSHIP_PLANS = {
    'Plus': {'price': 90, 'matches': 50, 'stars': 200},
    'VIP': {'price': 180, 'matches': 100, 'stars': 400},
    'Unlimited': {'price': 700, 'matches': "Sınırsız", 'stars': 1600}
}

def db_connection():
    connection = pymysql.connect(
        host='178.211.130.154',
        port=8888,
        user='shopiertest_usr',
        password='4h8Xv1aWMyRYjakr',
        database='shopierTest'
    )
    return connection

async def send_json_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Bu komutu kullanma yetkiniz yok.")
        return

    try:
        # JSON dosyasını gönder
        with open("kullanici.json", "rb") as file:
            if file.readable():
                await context.bot.send_document(chat_id=update.effective_chat.id, document=file, filename="kullanici.json")
            else:
                await update.message.reply_text("Dosya okunamadı.")
    except FileNotFoundError:
        await update.message.reply_text("Kullanici.json dosyası bulunamadı.")
    except Exception as e:
        await update.message.reply_text("Dosya gönderilirken bir hata oluştu.")
        print(f"JSON dosyası gönderilemedi: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id in banned_users:
        await update.message.reply_text("Üzgünüz, bu bottan yasaklandınız.")
        return

    all_users.add(user.id)
    if user.id not in user_matches:
        user_matches[user.id] = 999

    # Referral kontrolü
    if context.args and context.args[0].isdigit() and int(context.args[0]) != user.id:
        referrer_id = int(context.args[0])
        if referrer_id in referrals:
            referrals[referrer_id] += 1
        else:
            referrals[referrer_id] = 1
        
        # 2 referans kontrolü
        if referrals[referrer_id] == 2:
            await context.bot.send_message(
                chat_id=referrer_id,
                text="Tebrikler! 2 referansa ulaştınız. Kazandığınız Star'ların %5'unu bonus olarak almak için lütfen @anonimsohbetbotudestek ile iletişime geçin."
            )
        
        await update.message.reply_text(f"Sizi davet eden kullanıcıya 1 referans puanı eklendi!")

    start_message = """Partner aramaya hoşgeldin
/bul -- yeni partner bulur
/siradaki -- sohbeti durdurur ve yeni eşleşme arar
/stop -- eşleşmeyi durdurur.

Mesaj, gif, sticker, fotoğraf, video ya da sesli mesajları diyalog halinde olduğun partnere anonim şekilde gönderebilirim."""

    await update.message.reply_text(start_message)
    keyboard = [
        [InlineKeyboardButton("Erkek", callback_data='gender_male'),
         InlineKeyboardButton("Kadın", callback_data='gender_female')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Lütfen cinsiyetinizi seçiniz:', reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data.startswith('feedback_'):
        await handle_feedback(update, context)
    elif query.data.startswith('report_'):
        if query.data.startswith('report_category_'):
            await handle_report_category(update, context)
        else:
            await handle_report(update, context)

    if query.data.startswith('gender_'):
        gender = query.data.split('_')[1]
        user_genders[query.from_user.id] = gender
        if gender == 'female':
            keyboard = [[InlineKeyboardButton("Eşleşmeye Başla", callback_data='start_matching')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text('Eşleşmeye başlamak için butona basınız:', reply_markup=reply_markup)
        else:
            keyboard = [
                [InlineKeyboardButton("18-30", callback_data='age_18-30')],
                [InlineKeyboardButton("30+", callback_data='age_30+')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text('Yaş aralığınızı seçiniz:', reply_markup=reply_markup)
    elif query.data.startswith('age_'):
        keyboard = [
            [InlineKeyboardButton("Eşleşmeye Başla", callback_data='start_matching')],
            [InlineKeyboardButton("Özel Eşleşme", callback_data='special_matching')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text('Eşleşmeye başlamak için butona basınız:', reply_markup=reply_markup)
    elif query.data == 'start_matching':
        await start_matching(update, context)
    elif query.data == 'special_matching':
        keyboard = [
            [InlineKeyboardButton(f'Plus Üyelik ({MEMBERSHIP_PLANS["Plus"]["stars"]} Star)', callback_data='plus_membership')],
            [InlineKeyboardButton(f'VIP Üyelik ({MEMBERSHIP_PLANS["VIP"]["stars"]} Star)', callback_data='vip_membership')],
            [InlineKeyboardButton(f'Sınırsız Üyelik ({MEMBERSHIP_PLANS["Unlimited"]["stars"]} Star)', callback_data='unlimited_membership')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text('Premium kullanıcı olmanın avantajları:\n📌 Reklam yok \n🔎 Premium kullanıcılara reklam göstermiyoruz\n📌 Cinsiyete göre arama\n🔎 Premium kullanıcılar partnerlerini cinsiyete göre arayabilir\n📌 Sohbeti destekle\n🔎 Premium aboneliğin en değerli kısmı budur.\nBizi ne kadar çok desteklerseniz, o kadar az reklam göndeririz', reply_markup=reply_markup)
    elif query.data.endswith('_membership'):
        await handle_membership_purchase(update, context)

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id in banned_users:
        await update.message.reply_text("Üzgünüz, bu bottan yasaklandınız.")
        return

    if update.effective_chat.type != "private":
        return  # Grup içinde hiçbir yanıt verme
    
    if user.id in matches:
        # Sadece fotoğraf için kontrol yok
        if update.message.photo:
            await forward_message(update, context)
            return
        
        # Diğer medya türleri için kontrol
        if update.message.video or update.message.voice or update.message.audio or update.message.document or update.message.sticker:
            if user_memberships.get(user.id) not in ['Plus', 'VIP', 'Unlimited']:
                await update.message.reply_text("Üzgünüz, üyeliği olmayan kullanıcılar sadece fotoğraf gönderebilir. Lütfen bir üyelik planı satın alın.")
                return
        
        await forward_message(update, context)
    elif update.message.text and update.message.text.startswith('/'):
        await handle_commands(update, context)
    else:
        await update.message.reply_text("Şu anda aktif bir eşleşmeniz yok. Yeni bir eşleşme için /bul komutunu kullanabilirsiniz.")


async def send_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Sadece admin grubunda çalışacak şekilde kontrol
    if update.effective_chat.id != ADMIN_GROUP_ID:
        await update.message.reply_text("Bu komut sadece admin grubunda kullanılabilir.")
        return

    # İstatistikleri hazırla
    total_users = len(all_users)
    admin_count = len(AUTHORIZED_USERS)
    active_matches = len(matches) // 2  # Her eşleşme iki kullanıcı içerdiği için 2'ye bölüyoruz
    waiting_users_count = len(waiting_users['male']) + len(waiting_users['female'])
    banned_users_count = len(banned_users)

    # Ayarlar menüsünü oluştur
    settings_message = f"""🔧 Bot Ayarları ve İstatistikleri

👥 Kullanıcı İstatistikleri:
• Toplam Kullanıcı: {total_users}
• Aktif Eşleşmeler: {active_matches}
• Bekleyen Kullanıcılar: {waiting_users_count}
• Yasaklı Kullanıcılar: {banned_users_count}

👮 Yönetim:
• Admin Sayısı: {admin_count}

📝 Kullanılabilir Komutlar:
• /kayit - Tutulan tüm loglar gösterilir.
• /yayin - Tüm kullanıcılara reklam gönder
• /ban - Kullanıcı yasakla
• /ekle - Üyelik ekle
• /users - Kullanıcı sayısını göster

⚙️ Otomatik Bildirimler:
• Her 2 saatte bir bu istatistikler gruba gönderilir
"""

    await update.message.reply_text(settings_message)
last_status_update = datetime.now()

async def send_periodic_status(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Her 2 saatte bir admin grubuna durum güncellemesi gönderir"""
    global last_status_update
    
    # 2 saat geçip geçmediğini kontrol et
    current_time = datetime.now()
    if current_time - last_status_update < timedelta(hours=2):
        return

    # İstatistikleri hazırla
    total_users = len(all_users)
    admin_count = len(AUTHORIZED_USERS)
    active_matches = len(matches) // 2
    waiting_users_count = len(waiting_users['male']) + len(waiting_users['female'])
    banned_users_count = len(banned_users)

    status_message = f"""📊 Otomatik Durum Raporu
⏰ {current_time.strftime('%Y-%m-%d %H:%M')}

👥 Kullanıcı Durumu:
• Toplam Kullanıcı: {total_users}
• Aktif Eşleşmeler: {active_matches}
• Bekleyen Kullanıcılar: {waiting_users_count}
• Yasaklı Kullanıcılar: {banned_users_count}

👮 Yönetim Durumu:
• Admin Sayısı: {admin_count}
"""

    try:
        await context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=status_message)
        last_status_update = current_time
    except Exception as e:
        logger.error(f"Otomatik durum güncellemesi gönderilemedi: {str(e)}")


async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    receiver_id = matches.get(user.id)

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    receiver_id = matches.get(user.id)

    if not receiver_id:
        await update.message.reply_text("Üzgünüz, şu anda aktif bir eşleşmeniz yok.")
        return

    if update.message.text and update.message.text == '/siradaki':
        await next_match(update, context)
        return

    is_media = (update.message.photo or update.message.video or 
                update.message.audio or update.message.voice or 
                update.message.document or update.message.sticker)

    if is_media and user_memberships.get(user.id) not in ['VIP', 'Unlimited']:
        await update.message.reply_text("Üzgünüz, medya göndermek için VIP veya Sınırsız üyelik gereklidir.")
        return

    try:
        await context.bot.copy_message(
            chat_id=receiver_id, 
            from_chat_id=update.effective_chat.id, 
            message_id=update.message.message_id
        )
    except Exception as e:
        logger.error(f"Mesaj iletilirken hata oluştu: {str(e)}")
        await update.message.reply_text("Mesajınız iletilemedi. Lütfen daha sonra tekrar deneyin.")

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query
    if query.invoice_payload.startswith('membership_'):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Bir şeyler ters gitti...")

async def admin_users_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Bu komutu kullanma yetkiniz yok.")
        return

    total_users = len(all_users)
    await update.message.reply_text(f"Start veren toplam kullanıcı sayısı: {total_users}")


async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    payment = update.message.successful_payment
    user = update.effective_user
    membership_type = payment.invoice_payload.split('_')[1]
    
    # Üyelik türüne göre star miktarını al
    stars_spent = MEMBERSHIP_PLANS[membership_type]['stars']
    
    # Kullanıcının mevcut üyelik bilgilerini güncelle
    if user.id in user_memberships:
        user_memberships[user.id]['type'] = membership_type
        user_memberships[user.id]['stars_spent'] += stars_spent
    else:
        user_memberships[user.id] = {
            "type": membership_type,
            "stars_spent": stars_spent
        }
    
    # Kullanıcının eşleşme haklarını güncelle
    user_matches[user.id] = MEMBERSHIP_PLANS[membership_type]['matches']
    
    # JSON dosyasına kaydet
    save_to_json()
    
    await update.message.reply_text(f"{membership_type} üyeliğiniz başarıyla aktifleştirildi!")
    
    admin_message = f"Yeni üyelik alındı!\nKullanıcı ID: {user.id}\nÜyelik Türü: {membership_type}\nÖdeme Yöntemi: Star\nHarcanan Star: {stars_spent}"
    await context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=admin_message)


async def handle_membership_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user = query.from_user
    membership_type = query.data.split('_')[0].capitalize()
    if membership_type == 'Vip':
        membership_type = 'VIP'

    plan = MEMBERSHIP_PLANS[membership_type]
    
    keyboard = [
        [InlineKeyboardButton(f"Star ile Öde ({plan['stars']} Star)", callback_data=f"pay_star_{membership_type}")],
        [InlineKeyboardButton("Manuel Öde", url="https://t.me/anonimsohbetbotudestek")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"{membership_type} Üyelik\n"
        f"Fiyat: {plan['price']} TL\n"
        f"Eşleşme Hakkı: {'Sınırsız' if membership_type == 'Unlimited' else plan['matches']}\n"
        "Lütfen ödeme yöntemini seçin:",
        reply_markup=reply_markup
    )

async def handle_star_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    _, membership_type = query.data.split('_')[1:]
    plan = MEMBERSHIP_PLANS[membership_type]

    title = f"{membership_type} Üyelik"
    description = f"{'Sınırsız' if membership_type == 'Unlimited' else plan['matches']} eşleşme hakkı"
    payload = f"membership_{membership_type}"
    currency = "XTR"
    price = plan['stars']
    prices = [LabeledPrice(f"{membership_type} Üyelik", price * 1)]  # Price in cents

    await context.bot.send_invoice(
        chat_id=query.from_user.id,
        title=title,
        description=description,
        payload=payload,
        provider_token="1877036958:TEST:af0ac6bf4109f74c7824e92a205234473b5745df",
        currency=currency,
        prices=prices,
        start_parameter="start_parameter"
    )

async def admin_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Bu komutu kullanma yetkiniz yok.")
        return

    try:
        user_id = int(context.args[0])
        banned_users.add(user_id)

        if user_id in matches:
            partner_id = matches.pop(user_id, None)
            if partner_id:
                matches.pop(partner_id, None)
                await context.bot.send_message(chat_id=partner_id, text='Eşleştiğiniz kişi sohbetten ayrıldı. /bul yaparak yeni partner bulabilirsiniz.')

        for gender in ['male', 'female']:
            if user_id in waiting_users[gender]:
                waiting_users[gender].remove(user_id)

        # Veritabanına yasaklı kullanıcıyı kaydet
        connection = db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO banned_users (user_id, ban_date) VALUES (%s, %s)"
                cursor.execute(sql, (user_id, datetime.now()))
            connection.commit()
        finally:
            connection.close()

        # Kullanıcıyı yasaklandıktan sonra JSON dosyasına kaydet
        save_to_json()

        await update.message.reply_text(f"Kullanıcı ID {user_id} başarıyla yasaklandı.")
    except (IndexError, ValueError):
        await update.message.reply_text("Geçersiz komut. Doğru kullanım: /ban [kullanıcı_id]")


def load_banned_users():
    connection = db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT user_id FROM banned_users"
            cursor.execute(sql)
            result = cursor.fetchall()
            for row in result:
                banned_users.add(row['user_id'])
    finally:
        connection.close()


async def handle_commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command = update.message.text.split()[0].lower()
    if command == '/bul':
        await start_matching(update, context)
    elif command == '/siradaki':
        await next_match(update, context)

async def match_users(context: ContextTypes.DEFAULT_TYPE) -> None:
    while len(waiting_users['male']) > 0 and len(waiting_users['female']) > 0:
        male_id = waiting_users['male'].pop(0)
        female_id = waiting_users['female'].pop(0)

        if user_matches[male_id] > 0 and user_matches[female_id] > 0:
            matches[male_id] = female_id
            matches[female_id] = male_id

            if user_memberships.get(male_id) != 'Unlimited':
                user_matches[male_id] -= 1
            if user_memberships.get(female_id) != 'Unlimited':
                user_matches[female_id] -= 1

            base_message = """Eşleştiniz! Diğer kişiyle sohbet edebilirsiniz.

Kullanabileceğiniz komutlar:
/siradaki -- sohbeti durdurur ve yeni eşleşme arar
/stop -- eşleşmeyi durdurur
/vip -- Cinsiyete ve yaşa göre ara"""

            # Check memberships and create custom messages
            male_message = base_message
            female_message = base_message

            male_membership = user_memberships.get(male_id)
            female_membership = user_memberships.get(female_id)

            if male_membership in [  'Unlimited']:
                female_message = f"🌟 {male_membership} üyesi ile eşleştiniz!\n\n" + base_message
            
            if female_membership in ['Unlimited']:
                male_message = f"🌟 {female_membership} üyesi ile eşleştiniz!\n\n" + base_message

            await context.bot.send_message(chat_id=male_id, text=male_message)
            await context.bot.send_message(chat_id=female_id, text=female_message)

            logger.info(f"Eşleşme: Kullanıcı {male_id} ve Kullanıcı {female_id} eşleşti.")
        else:
            if user_matches[male_id] == 0:
                await send_membership_info(context, male_id)
            if user_matches[female_id] == 0:
                await send_membership_info(context, female_id)

async def send_membership_info(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    message = "Merhaba, hakkınız bitmiştir. Lütfen aşağıdaki planı inceleyiniz:\n\n"
    message += "Satış planı şu şekildedir:\n"
    for plan, details in MEMBERSHIP_PLANS.items():
        message += f"- {plan} Üyelik: {details['price']} TL, "
        message += f"{'sınırsız' if plan == 'Unlimited' else details['matches']} eşleşme hakkı\n"
    
    keyboard = [
        [InlineKeyboardButton(f"{plan} Üyelik ({details['price']} TL)", callback_data=f"{plan.lower()}_membership")]
        for plan, details in MEMBERSHIP_PLANS.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(chat_id=user_id, text=message, reply_markup=reply_markup)

async def start_matching(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id in banned_users:
        await send_message(update, "Üzgünüz, bu bottan yasaklandınız.")
        return

    gender = user_genders.get(user.id)

    if not gender:
        keyboard = [
            [InlineKeyboardButton('Erkek', callback_data='gender_male'),
             InlineKeyboardButton('Kadın', callback_data='gender_female')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await send_message(update, 'Lütfen cinsiyetinizi seçin:', reply_markup=reply_markup)
        return

    if user.id not in waiting_users[gender]:
        if user_matches[user.id] > 0:
            waiting_users[gender].append(user.id)
            await send_message(update, 'Eşleşme aranmaya başladı. Lütfen bekleyin...')
            await match_users(context)
        else:
            await send_membership_info(context, user.id)
    else:
        await send_message(update, 'Zaten eşleşme sırasındasınız.')
async def send_message(update: Update, text: str, reply_markup: InlineKeyboardMarkup = None):
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)


async def set_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    gender = query.data.split('_')[-1]
    user_genders[query.from_user.id] = gender

    if gender == 'male':
        keyboard = [
            [InlineKeyboardButton('18-30', callback_data='age_18-30')],
            [InlineKeyboardButton('30+', callback_data='age_30+')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text('Yaş aralığınızı seçiniz:', reply_markup=reply_markup)
    else:  # female
        await start_matching(update, context)

async def set_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    age_range = query.data.split('_')[-1]
    # Burada yaş aralığını kaydedebilirsiniz, şu an için bir şey yapmıyoruz
    await start_matching(update, context)

async def next_match(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id in banned_users:
        await update.message.reply_text("Üzgünüz, bu bottan yasaklandınız.")
        return
    
    if user.id in matches:
        partner_id = matches.pop(user.id, None)
        if partner_id:
            matches.pop(partner_id, None)
            await context.bot.send_message(chat_id=partner_id, text='Eşleştiğiniz kişi sohbetten ayrıldı. /bul yaparak yeni partner bulabilirsiniz.')
        
        keyboard = [
            [InlineKeyboardButton('👍 Evet', callback_data=f'feedback_yes_{partner_id}'),
             InlineKeyboardButton('👎 Hayır', callback_data=f'feedback_no_{partner_id}')],
            [InlineKeyboardButton('🚫 Bildir', callback_data=f'report_{partner_id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Bu konuşmadan memnun kaldınız mı?', reply_markup=reply_markup)
        
        # Yeni eşleşme başlat
        await start_matching(update, context)
    elif user.id in waiting_users['male'] or user.id in waiting_users['female']:
        await update.message.reply_text('Zaten eşleşme sırasındasınız.')
    else:
        await update.message.reply_text('Aktif bir eşleşmeniz yok. /bul komutunu kullanarak yeni bir eşleşme arayabilirsiniz.')


async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    feedback, partner_id = query.data.split('_')[1:]
    sender_id = query.from_user.id

    feedback_text = f"Kullanıcı {sender_id} son konuşması hakkında {'olumlu' if feedback == 'yes' else 'olumsuz'} geri bildirim verdi. Eşleştiği kişi: {partner_id}"
    
    await context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=feedback_text)
    await query.edit_message_text("Geri bildiriminiz için teşekkürler!")


async def handle_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    partner_id = query.data.split('_')[1]

    report_categories = [
        'İllegallik',
        'Hakaret',
        'Reklam ve dilencilik'
    ]

    keyboard = [
        [InlineKeyboardButton(category, callback_data=f'report_category_{category}_{partner_id}')]
        for category in report_categories
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text('Lütfen bildirim nedeninizi seçin:', reply_markup=reply_markup)


async def handle_report_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    category, partner_id = query.data.split('_')[2:]
    sender_id = query.from_user.id

    report_text = f"Kullanıcı {sender_id}, {partner_id} ID'li kullanıcıyı '{category}' nedeniyle bildirdi."
    
    await context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=report_text)
    await query.edit_message_text("Bildiriminiz alınmıştır. Teşekkür ederiz!")

async def stop_matching(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id in banned_users:
        await update.message.reply_text("Üzgünüz, bu bottan yasaklandınız.")
        return
    
    if user.id in matches:
        partner_id = matches.pop(user.id, None)
        if partner_id:
            matches.pop(partner_id, None)
            await context.bot.send_message(chat_id=partner_id, text='Eşleştiğiniz kişi sohbetten ayrıldı. /bul yaparak yeni partner bulabilirsiniz.')
    
    for gender in ['male', 'female']:
        if user.id in waiting_users[gender]:
            waiting_users[gender].remove(user.id)
    
    await update.message.reply_text("Eşleşme durduruldu. Yeniden eşleşmek istediğinizde /bul komutunu kullanabilirsiniz.")


async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Bu komutu kullanma yetkiniz yok.")
        return

    ad_text = ' '.join(context.args)
    if not ad_text:
        await update.message.reply_text("Lütfen reklam metnini girin. Örnek: /yayın Merhaba, yeni özelliğimiz!")
        return

    # Send initial status message to admin group
    status_message = await context.bot.send_message(
        chat_id=ADMIN_GROUP_ID,
        text="🚀 Reklam gönderimi başlatılıyor..."
    )

    sent_count = 0
    skipped_count = 0
    failed_count = 0

    # Gerçekten mesajı yönlendireceğiz
    ad_message = await context.bot.send_message(
        chat_id=ADMIN_GROUP_ID,
        text=ad_text
    )

    for user_id in all_users:
        # Skip users with premium memberships
        if user_id in user_memberships and user_memberships[user_id] in ['Plus', 'VIP', 'Unlimited']:
            skipped_count += 1
            continue

        try:
            # Mesajı gerçekten yönlendir
            await context.bot.forward_message(chat_id=user_id, from_chat_id=ADMIN_GROUP_ID, message_id=ad_message.message_id)
            sent_count += 1

            # Update status message every 50 users
            if sent_count % 50 == 0:
                await status_message.edit_text(
                    f"📤 Reklam gönderimi devam ediyor...\n"
                    f"✅ Gönderilen: {sent_count}\n"
                    f"⏭️ Atlanan (Premium): {skipped_count}\n"
                    f"❌ Başarısız: {failed_count}"
                )

        except Exception as e:
            failed_count += 1
            logger.error(f"Hata: Kullanıcı {user_id}'ye mesaj gönderilemedi. Hata: {str(e)}")

    # Final status update
    final_report = (
        f"📊 Reklam Gönderim Raporu\n\n"
        f"✅ Başarıyla gönderilen: {sent_count}\n"
        f"⏭️ Atlanan premium kullanıcı: {skipped_count}\n"
        f"❌ Başarısız gönderim: {failed_count}\n"
        f"📝 Toplam hedeflenen: {len(all_users)}\n\n"
        f"📨 Gönderilen Reklam Metni:\n{ad_text}"
    )

    await status_message.edit_text(final_report)




async def vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id in banned_users:
        await update.message.reply_text("Üzgünüz, bu bottan yasaklandınız.")
        return

    vip_info = """👑 VIP Özellikler👑:
    
Premium kullanıcı olmanın avantajları:

📌 Reklam yok
🔎 Premium kullanıcılara reklam göstermiyoruz

📌 Cinsiyete göre arama
🔎 Premium kullanıcılar partnerlerini cinsiyete göre arayabilir

📞7/24 Canlı destekten faydalanma

📌 Sohbeti destekle
🔎 Premium aboneliğin en değerli kısmı budur.
Bizi ne kadar çok desteklerseniz, o kadar az reklam göndeririz

💎 Sadece premium değil, aynı zamanda benzersiz bir VIP kullanıcı olmak istiyorsanız aşağıda ki ödeme sistemimize göz atın :

Üyelik seçenekleri:"""

    await update.message.reply_text(vip_info)

    keyboard = [
        [InlineKeyboardButton(f"Plus Üyelik ({MEMBERSHIP_PLANS['Plus']['stars']} Star)", callback_data='plus_membership')],
        [InlineKeyboardButton(f"VIP Üyelik ({MEMBERSHIP_PLANS['VIP']['stars']} Star)", callback_data='vip_membership')],
        [InlineKeyboardButton(f"Sınırsız Üyelik ({MEMBERSHIP_PLANS['Unlimited']['stars']} Star)", callback_data='unlimited_membership')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Lütfen üyelik planı seçin:", reply_markup=reply_markup)

async def klavuz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Botun işlevlerini listeleyen komut."""
    guide_message = (
        "Bu botun işlevleri:\n"
        "/start - Botu başlatır ve tanıtır.\n"
        "/bul - Yeni bir partner bulur.\n"
        "/siradaki - Mevcut eşleşmeyi durdurur ve yeni eşleşme arar.\n"
        "/stop - Eşleşmeyi durdurur.\n"
        "/kayit - Kullanıcı kayıt dosyasını gönderir.\n"
        "/ekle - Kullanıcıya üyelik ekler.\n"
        "/ban - Kullanıcıyı yasaklar.\n"
        "/yayin - Kullanıcılara reklam gönderir.\n"
        "/ref - Referans bilgilerini gösterir.\n"
        "/myref - Kişisel referans istatistiklerini gösterir.\n"
        "/klavuz - Bu kılavuzu gösterir."
    )
    await update.message.reply_text(guide_message)

async def sahip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Bu komutu kullanma yetkiniz yok.")
        return

    # Star ile ödeme yapan kullanıcı sayısı
    total_registered = len(user_memberships)

    # Toplam bilanço (star sayısı)
    total_stars = sum(MEMBERSHIP_PLANS[membership]['stars'] for membership in user_memberships.values())

    # Giderlerin hesaplanması
    developer_pay = total_stars * 0.05      # %5 Yazılımcı Payı
    referrals_pay = total_stars * 0.15      # %15 Referanslar Payı
    refler_pay = total_stars * 0.05          # %5 Refler Payı
    play_store_cut = total_stars * 0.33      # %33 Play Store Kesintisi
    tax_cut = total_stars * 0.15             # %15 Vergi Kesintisi

    # Toplam gider
    total_expenses = developer_pay + referrals_pay + refler_pay + play_store_cut + tax_cut

    # Kalan starlar
    remaining_stars = total_stars - total_expenses

    # İstatistik mesajının hazırlanması
    message = (
        f"🔹 **Sahip İstatistikleri** 🔹\n\n"
        f"👥 **Kayıtlı Kullanıcılar:** {total_registered} kişi (Star ile ödeme yapanlar)\n\n"
        f"💰 **Toplam Bilanço:** {total_stars:.2f} Star\n\n"
        f"💸 **Giderler:**\n"
        f"• %5 Yazılımcı Payı: {developer_pay:.2f} Star\n"
        f"• %15 Referanslar Payı: {referrals_pay:.2f} Star\n"
        f"• %5 Refler Payı: {refler_pay:.2f} Star\n"
        f"• %33 Play Store Kesintisi: {play_store_cut:.2f} Star\n"
        f"• %15 Vergi Kesintisi: {tax_cut:.2f} Star\n\n"
        f"💼 **Kalan Starlar:** {remaining_stars:.2f} Star"
    )

    await update.message.reply_text(message, parse_mode='Markdown')



def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    # Sadece özel sohbetlerde çalışacak komutlar
    application.add_handler(CommandHandler("ref", ref, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("myref", myref, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("stop", stop_matching, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("start", start, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("bul", start_matching, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("siradaki", next_match, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("kayit", send_json_file, filters=filters.Chat(chat_id=ADMIN_GROUP_ID)))
    application.add_handler(CommandHandler("vip", vip_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("klavuz", klavuz))
    application.add_handler(CommandHandler("sahip", sahip, filters=filters.Chat(chat_id=ADMIN_GROUP_ID)))

    # Sadece admin grubunda çalışacak komutlar
    application.add_handler(CommandHandler("ban", admin_ban_user, filters=filters.Chat(chat_id=ADMIN_GROUP_ID)))
    application.add_handler(CommandHandler("yayin", send_broadcast, filters=filters.Chat(chat_id=ADMIN_GROUP_ID)))  # Güncelleme burada
    application.add_handler(CommandHandler("users", admin_users_count, filters=filters.Chat(chat_id=ADMIN_GROUP_ID)))
    application.add_handler(CommandHandler("ayarlar", send_settings_menu, filters=filters.Chat(chat_id=ADMIN_GROUP_ID)))

    # Star ödeme butonu için handler
    application.add_handler(CallbackQueryHandler(handle_star_payment, pattern='^pay_star_'))  # Herkese açık kalacak

    # Diğer handler'lar
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CallbackQueryHandler(handle_membership_purchase, pattern='^(plus|vip|unlimited)_membership$'))
    application.add_handler(CallbackQueryHandler(handle_feedback, pattern='^feedback_'))
    application.add_handler(CallbackQueryHandler(handle_report, pattern='^report_'))
    application.add_handler(CallbackQueryHandler(handle_report_category, pattern='^report_category_'))

    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_messages))

    # Admin handler'ları ekle
    add_admin_handlers(application)

    application.run_polling()

if __name__ == '__main__':
    main()
