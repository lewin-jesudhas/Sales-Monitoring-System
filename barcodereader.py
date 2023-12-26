from pyzbar import pyzbar
import cv2

def draw_barcode(decoded, image):
    image = cv2.rectangle(image, (decoded.rect.left, decoded.rect.top), 
                            (decoded.rect.left + decoded.rect.width, decoded.rect.top + decoded.rect.height),
                            color=(0, 255, 0),
                            thickness=5)
    return image

def decode(image):
    decoded_objects = pyzbar.decode(image)
    for obj in decoded_objects:
        image = draw_barcode(obj, image)
        #print("Type:", obj.type)
        
        print("Data:", obj.data)
        print()

    return image, decoded_objects  # Return both image and decoded_objects

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    while True:
        _, frame = cap.read()
        frame, decoded_objects = decode(frame)  # Unpack both image and decoded_objects
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) == ord("q"):
            break
