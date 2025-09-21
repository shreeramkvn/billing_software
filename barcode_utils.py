import cv2
import sys
import os
from tkinter import messagebox, simpledialog
import tkinter as tk
from PIL import ImageGrab
import tempfile

# Check if we're running as a PyInstaller bundle
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = sys._MEIPASS
else:
    # Running as Python script
    application_path = os.path.dirname(os.path.abspath(__file__))

# Try to add the DLL directory to the path
try:
    os.add_dll_directory(application_path)
except AttributeError:
    # For older Python versions
    os.environ['PATH'] = application_path + os.pathsep + os.environ['PATH']

class BarcodeScanner:
    def __init__(self):
        self.scanner_active = False
        self.zbar_available = self.check_zbar_availability()
    
    def check_zbar_availability(self):
        """Check if zbar library is available"""
        try:
            # Try to import and use pyzbar
            from pyzbar.pyzbar import decode
            # Test with a simple decode
            decode(b'test')
            return True
        except (ImportError, OSError, Exception) as e:
            print(f"ZBar not available: {e}")
            return False
    
    def scan_from_webcam(self):
        """Scan barcode using webcam"""
        if not self.zbar_available:
            return self.scan_from_webcam_fallback()
        
        try:
            cap = cv2.VideoCapture(0)
            detected_barcode = None
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Find and decode barcodes
                from pyzbar.pyzbar import decode
                barcodes = decode(frame)
                for barcode in barcodes:
                    barcode_data = barcode.data.decode("utf-8")
                    barcode_type = barcode.type
                    
                    # Draw rectangle around barcode
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
                    # Put barcode data on frame
                    text = f"{barcode_type}: {barcode_data}"
                    cv2.putText(frame, text, (x, y - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    detected_barcode = barcode_data
                
                # Show frame
                cv2.imshow("Barcode Scanner", frame)
                
                # Exit if barcode detected or 'q' pressed
                if detected_barcode or cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            return detected_barcode
        except Exception as e:
            print(f"Error in barcode scanning: {e}")
            return self.scan_from_webcam_fallback()
    
    def scan_from_webcam_fallback(self):
        """Fallback method if zbar is not available"""
        root = tk.Tk()
        root.withdraw()
        
        result = simpledialog.askstring(
            "Barcode Input", 
            "Barcode scanning is not available. Please enter barcode manually:",
            parent=root
        )
        
        root.destroy()
        return result
    
    def scan_from_keyboard(self):
        """Simulate barcode scanner as keyboard input"""
        print("Please scan barcode...")
        return input()
    
    def scan_from_image(self, image_path):
        """Scan barcode from image file"""
        if not self.zbar_available:
            return None
        
        try:
            from pyzbar.pyzbar import decode
            image = cv2.imread(image_path)
            barcodes = decode(image)
            
            if barcodes:
                return barcodes[0].data.decode("utf-8")
            return None
        except Exception:
            return None
    
    def scan_from_clipboard(self):
        """Scan barcode from clipboard image"""
        if not self.zbar_available:
            return None
        
        try:
            from pyzbar.pyzbar import decode
            # Get image from clipboard
            image = ImageGrab.grabclipboard()
            if image:
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                image.save(temp_file.name)
                temp_file.close()
                
                # Scan barcode from temp file
                barcode = self.scan_from_image(temp_file.name)
                
                # Clean up
                os.unlink(temp_file.name)
                
                return barcode
            return None
        except Exception:
            return None

# import cv2
# from pyzbar import pyzbar
# import keyboard
# from PIL import ImageGrab
# import tempfile
# import os

# class BarcodeScanner:
#     def __init__(self):
#         self.scanner_active = False
    
#     def scan_from_webcam(self):
#         """Scan barcode using webcam"""
#         cap = cv2.VideoCapture(0)
#         detected_barcode = None
        
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break
            
#             # Find and decode barcodes
#             barcodes = pyzbar.decode(frame)
#             for barcode in barcodes:
#                 barcode_data = barcode.data.decode("utf-8")
#                 barcode_type = barcode.type
                
#                 # Draw rectangle around barcode
#                 (x, y, w, h) = barcode.rect
#                 cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
#                 # Put barcode data on frame
#                 text = f"{barcode_type}: {barcode_data}"
#                 cv2.putText(frame, text, (x, y - 10), 
#                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
#                 detected_barcode = barcode_data
            
#             # Show frame
#             cv2.imshow("Barcode Scanner", frame)
            
#             # Exit if barcode detected or 'q' pressed
#             if detected_barcode or cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
        
#         cap.release()
#         cv2.destroyAllWindows()
#         return detected_barcode
    
#     def scan_from_keyboard(self):
#         """Simulate barcode scanner as keyboard input"""
#         print("Please scan barcode...")
#         # Barcode scanners typically send data as keyboard input followed by Enter
#         # This is a simplified version - in practice, you'd need to capture the input
#         # and detect when a barcode has been scanned
#         return input()
    
#     def scan_from_image(self, image_path):
#         """Scan barcode from image file"""
#         image = cv2.imread(image_path)
#         barcodes = pyzbar.decode(image)
        
#         if barcodes:
#             return barcodes[0].data.decode("utf-8")
#         return None
    
#     def scan_from_clipboard(self):
#         """Scan barcode from clipboard image"""
#         # Get image from clipboard
#         image = ImageGrab.grabclipboard()
#         if image:
#             # Save to temporary file
#             temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
#             image.save(temp_file.name)
#             temp_file.close()
            
#             # Scan barcode from temp file
#             barcode = self.scan_from_image(temp_file.name)
            
#             # Clean up
#             os.unlink(temp_file.name)
            
#             return barcode
#         return None