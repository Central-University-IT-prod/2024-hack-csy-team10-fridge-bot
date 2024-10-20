import cv2


def read_qr(file_name: str):
    img = cv2.imread(file_name)
    detector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = detector.detectAndDecode(img)

    return data

# print(f"Данные из qr-кода: {data}")

# async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     new_file = await update.message.effective_attachment[-1].get_file()
#     file = await new_file.download_to_drive()
    
#     return file