import os
import shutil

def archive_old_main():
    """Tự động di chuyển file chính app.py ban đầu vào folder lưu trữ .archived để tái tổ chức gọn gàng"""
    os.makedirs('.archived', exist_ok=True)
    if os.path.exists('app.py') and not os.path.exists('.archived/app_original.py'):
        shutil.copy('app.py', '.archived/app_original.py')
        print("✓ Archived original app.py successfully into .archived/app_original.py")

if __name__ == '__main__':
    archive_old_main()
