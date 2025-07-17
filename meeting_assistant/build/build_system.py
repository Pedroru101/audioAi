import os
import subprocess
import json
import platform
import zipfile
from typing import List

# Ruta base del proyecto (ajusta si es necesario)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def detect_dependencies() -> List[str]:
    """Detecta dependencias de requirements.txt y requirements_ui.txt."""
    deps = []
    for req_file in ['requirements.txt', 'requirements_ui.txt']:
        path = os.path.join(PROJECT_ROOT, req_file)
        if os.path.exists(path):
            with open(path, 'r') as f:
                deps.extend([line.strip() for line in f if line.strip() and not line.startswith('#')])
    return deps

def generate_executable(spec_file: str, output_dir: str):
    """Genera ejecutable con PyInstaller."""
    cmd = ['pyinstaller', '--onefile', '--distpath', output_dir, spec_file]
    subprocess.run(cmd, check=True)
    print(f"Ejecutable generado en {output_dir}")

def create_installer(platform: str, executable_path: str, installer_output: str):
    """Crea instalador según plataforma (placeholders para NSIS/Inno Setup)."""
    if platform == 'windows':
        # Asume NSIS instalado; crea un script NSIS básico
        nsis_script = f"""
        OutFile "{installer_output}"
        InstallDir "$PROGRAMFILES\MeetingAssistantPro"
        Section
        SetOutPath $INSTDIR
        File "{executable_path}"
        SectionEnd
        """
        with open('temp.nsi', 'w') as f:
            f.write(nsis_script)
        subprocess.run(['makensis', 'temp.nsi'], check=True)
        os.remove('temp.nsi')
    elif platform == 'mac':
        # Placeholder: Usa platypus o similar para .app
        print("Instalador Mac: Implementar con platypus (instala via brew).")
    elif platform == 'linux':
        # Placeholder: Usa makeself o deb/rpm
        print("Instalador Linux: Implementar con makeself.")
    print(f"Instalador generado: {installer_output}")

def sign_executable(executable_path: str):
    """Firma digital (placeholder: necesita certificados reales)."""
    print(f"Firma placeholder para {executable_path}. Implementa con signtool (Windows) o codesign (Mac).")

def create_portable_version(executable_path: str, output_zip: str):
    """Genera versión portable en ZIP."""
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        zipf.write(executable_path, os.path.basename(executable_path))
        # Agrega configs y assets necesarios
        zipf.write(os.path.join(PROJECT_ROOT, 'config.json'), 'config.json')
    print(f"Versión portable: {output_zip}")

def main():
    deps = detect_dependencies()
    print(f"Dependencias detectadas: {deps}")
    
    # Carga config para versiones, etc.
    config_path = os.path.join(PROJECT_ROOT, 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    version = config.get('version', '1.0.0')
    
    output_dir = os.path.join(PROJECT_ROOT, 'dist')
    os.makedirs(output_dir, exist_ok=True)
    
    # Genera spec file básico para PyInstaller (basado en main_improved.py)
    spec_content = f"""
    from PyInstaller.utils.hooks import collect_data_files
    a = Analysis(['{os.path.join(PROJECT_ROOT, 'main_improved.py')}'],
                 datas=collect_data_files('meeting_assistant'),
                 hiddenimports={deps})
    pyz = PYZ(a.pure)
    exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, name='MeetingAssistantPro')
    """
    spec_path = os.path.join(output_dir, 'meeting_assistant.spec')
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    
    generate_executable(spec_path, output_dir)
    exe_path = os.path.join(output_dir, 'MeetingAssistantPro')
    
    sign_executable(exe_path)
    
    installer_output = os.path.join(output_dir, f'MeetingAssistantPro_{version}_setup.exe')  # Ejemplo para Windows
    create_installer(platform.system().lower(), exe_path, installer_output)
    
    portable_zip = os.path.join(output_dir, f'MeetingAssistantPro_{version}_portable.zip')
    create_portable_version(exe_path, portable_zip)

if __name__ == '__main__':
    main()