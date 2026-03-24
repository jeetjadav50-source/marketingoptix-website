import os
import django
from django.conf import settings
from django.template.loader import get_template
from django.template import TemplateSyntaxError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketingoptix.settings')
django.setup()

templates_dir = os.path.join(settings.BASE_DIR, 'user', 'templates')
errors = 0

for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            rel_path = os.path.relpath(os.path.join(root, file), templates_dir)
            try:
                # Need to use the template name relative to templates directory
                # But actually, Django template loaders use the name. 
                # Since 'user/templates' is in DIRS or app directories, usually simply 'file' or its rel path works.
                get_template(rel_path.replace('\\', '/'))
            except TemplateSyntaxError as e:
                print(f"Syntax Error in {rel_path}: {e}")
                errors += 1
            except Exception as e:
                print(f"Other Error in {rel_path}: {e}")
                errors += 1

if errors == 0:
    print("All templates syntax checked successfully!")
else:
    print(f"Found {errors} errors.")
