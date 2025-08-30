import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get('TOKEN')

# حالت‌های مکالمه
CHOOSING_DOOR_TYPE, ENTERING_WIDTH, ENTERING_HEIGHT, CHOOSING_MOTOR, NEED_INSTALLATION = range(5)

# قیمت هر متر مربع
PRICE_PER_SQUARE_METER = {
    "1": 1950000,
    "2": 2300000,
    "3": 3100000,
    "4": 3200000,
    "5": 2800000
}

# قیمت موتورها
MOTOR_PRICES = {
    "1": 5700000,
    "2": 6200000,
    "3": 4500000,
    "4": 4900000,
    "5": 5200000
}

async def start(update: Update, context):
    await update.message.reply_text(
        "به ربات آنلاین قیمت‌گذاری مجموعه ریما الومین خوش آمدید!\n"
        "لطفاً نوع درب را انتخاب کنید:\n"
        "1. تیغه قوس سبک (هر متر مربع 1,950,000 تومان)\n"
        "2. تیغه قوس وزن سنگین (هر متر مربع 2,300,000 تومان)\n"
        "3. لوکس 70 (هر متر مربع 3,100,000 تومان)\n"
        "4. لوکس 90 (هر متر مربع 3,200,000 تومان)\n"
        "5. تیغه 100 (هر متر مربع 2,800,000 تومان)\n"
        "شماره گزینه مورد نظر را وارد کنید یا /start را بزنید."
    )
    return CHOOSING_DOOR_TYPE

async def choose_door_type(update: Update, context):
    user_input = update.message.text
    if user_input in PRICE_PER_SQUARE_METER:
        context.user_data['door_type'] = user_input
        context.user_data['price_per_square_meter'] = PRICE_PER_SQUARE_METER[user_input]
        await update.message.reply_text("لطفاً عرض درب (برحسب سانتیمتر) را وارد کنید یا /start را بزنید.")
        return ENTERING_WIDTH
    elif user_input == "/start":
        return await start(update, context)
    else:
        await update.message.reply_text("گزینه نامعتبر! لطفاً شماره 1 تا 5 را انتخاب کنید یا /start را بزنید.")
        return CHOOSING_DOOR_TYPE

async def enter_width(update: Update, context):
    try:
        width_cm = float(update.message.text)
        context.user_data['width_cm'] = width_cm
        await update.message.reply_text("لطفاً ارتفاع درب (از کف تا زیرسقف + 20 سانتیمتر، برحسب سانتیمتر) را وارد کنید یا /start را بزنید.")
        return ENTERING_HEIGHT
    except ValueError:
        if update.message.text == "/start":
            return await start(update, context)
        await update.message.reply_text("لطفاً یک عدد معتبر (سانتیمتر) برای عرض وارد کنید یا /start را بزنید.")
        return ENTERING_WIDTH

async def enter_height(update: Update, context):
    try:
        height_cm = float(update.message.text)
        context.user_data['height_cm'] = height_cm
        width_cm = context.user_data['width_cm']
        total_area = (width_cm / 100) * (height_cm / 100)
        price_per_square_meter = context.user_data['price_per_square_meter']
        total_price_tiogh = total_area * price_per_square_meter
        context.user_data['total_price_tiogh'] = total_price_tiogh
        context.user_data['total_area'] = total_area
        await update.message.reply_text(
            f"عرض درب: {width_cm} سانتیمتر\n"
            f"ارتفاع درب: {height_cm} سانتیمتر\n"
            f"جمع ابعاد شما: {total_area:.2f} متر مربع\n"
            f"قیمت تیغه: {total_price_tiogh:,.0f} تومان\n"
            "لطفاً نوع موتور را انتخاب کنید:\n"
            "1. ساید 300 کیلو (قیمت: 5,700,000 تومان)\n"
            "2. ساید 600 کیلو (قیمت: 6,200,000 تومان)\n"
            "3. توبلار با متعلقات کامل تا 12 متر مربع (قیمت: 4,500,000 تومان)\n"
            "4. توبلار با متعلقات کامل تا 14 متر مربع (قیمت: 4,900,000 تومان)\n"
            "5. توبلار با متعلقات کامل تا 16 متر مربع (قیمت: 5,200,000 تومان)\n"
            "شماره گزینه مورد نظر را وارد کنید یا /start را بزنید."
        )
        return CHOOSING_MOTOR
    except ValueError:
        if update.message.text == "/start":
            return await start(update, context)
        await update.message.reply_text("لطفاً یک عدد معتبر (سانتیمتر) برای ارتفاع وارد کنید یا /start را بزنید.")
        return ENTERING_HEIGHT

async def choose_motor(update: Update, context):
    user_input = update.message.text
    if user_input in MOTOR_PRICES:
        context.user_data['motor_type'] = user_input
        context.user_data['motor_price'] = MOTOR_PRICES[user_input]
        await update.message.reply_text(
            f"نوع موتور انتخابی: {['ساید 300 کیلو', 'ساید 600 کیلو', 'توبلار با متعلقات کامل تا 12 متر مربع', 'توبلار با متعلقات کامل تا 14 متر مربع', 'توبلار با متعلقات کامل تا 16 متر مربع'][int(user_input) - 1]}\n"
            f"قیمت موتور: {context.user_data['motor_price']:,.0f} تومان\n"
            "نیاز به آهن‌آلات و نصب دارید؟ (بله/خیر) یا /start را بزنید."
        )
        return NEED_INSTALLATION
    elif user_input == "/start":
        return await start(update, context)
    else:
        await update.message.reply_text("گزینه نامعتبر! لطفاً شماره 1 تا 5 را انتخاب کنید یا /start را بزنید.")
        return CHOOSING_MOTOR

async def need_installation(update: Update, context):
    user_input = update.message.text.lower()
    total_area = context.user_data['total_area']
    if user_input == "بله":
        if total_area <= 15:
            installation_cost = 3700000
        elif total_area <= 25:
            installation_cost = 4500000
        else:
            installation_cost = 4500000
        context.user_data['installation_cost'] = installation_cost
        total_price_tiogh = context.user_data['total_price_tiogh']
        motor_price = context.user_data['motor_price']
        final_price = total_price_tiogh + motor_price + installation_cost
        await update.message.reply_text(
            f"هزینه نصب و آهن‌آلات: {installation_cost:,.0f} تومان\n"
            f"قیمت تیغه: {total_price_tiogh:,.0f} تومان\n"
            f"قیمت موتور: {motor_price:,.0f} تومان\n"
            f"قیمت نهایی درب شما: {final_price:,.0f} تومان\n"
            "در صورت مشاوره بیشتر با شماره 09132929386 (کرمی) تماس بگیرید.\nبرای محاسبه جدید، /start را بزنید."
        )
        return ConversationHandler.END
    elif user_input == "خیر":
        total_price_tiogh = context.user_data['total_price_tiogh']
        motor_price = context.user_data['motor_price']
        final_price = total_price_tiogh + motor_price
        await update.message.reply_text(
            f"قیمت تیغه: {total_price_tiogh:,.0f} تومان\n"
            f"قیمت موتور: {motor_price:,.0f} تومان\n"
            f"قیمت نهایی درب شما: {final_price:,.0f} تومان\n"
            "در صورت مشاوره بیشتر با شماره 09132929386 (کرمی) تماس بگیرید.\nبرای محاسبه جدید، /start را بزنید."
        )
        return ConversationHandler.END
    elif user_input == "/start":
        return await start(update, context)
    else:
        await update.message.reply_text("لطفاً بله یا خیر وارد کنید یا /start را بزنید!")
        return NEED_INSTALLATION

def main():
    application = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_DOOR_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_door_type)],
            ENTERING_WIDTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_width)],
            ENTERING_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_height)],
            CHOOSING_MOTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_motor)],
            NEED_INSTALLATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, need_installation)]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()