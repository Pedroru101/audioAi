"""
Script de construcción para Meeting Assistant Pro
Uso: python build.py [opciones]
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from build_config import *

class MeetingAssistantBuilder:
    def __init__(self, platform='windows', debug=False):
        self.platform = platform
        self.debug = debug
        self.spec_file = 'MeetingAssistantPro.spec'

    def clean_build(self):
        """Limpia directorios de construcción anteriores"""
        print("🧹 Limpiando construcciones anteriores...")
        for dir_path in [BUILD_DIR, DIST_DIR, TEMP_DIR]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                print(f"   ✓ Eliminado: {dir_path}")

        if os.path.exists(self.spec_file):
            os.remove(self.spec_file)
            print(f"   ✓ Eliminado: {self.spec_file}")

    def create_directories(self):
        """Crea directorios necesarios"""
        print("📁 Creando directorios...")
        for dir_path in [BUILD_DIR, DIST_DIR, TEMP_DIR, ASSETS_DIR]:
            os.makedirs(dir_path, exist_ok=True)
            print(f"   ✓ Creado: {dir_path}")

    def check_dependencies(self):
        """Verifica que todas las dependencias estén instaladas"""
        print("🔍 Verificando dependencias...")

        # Verificar PyInstaller
        try:
            import PyInstaller
            print("   ✓ PyInstaller instalado")
        except ImportError:
            print("   ❌ PyInstaller no encontrado. Instalando...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

        # Verificar otras dependencias
        missing_deps = []
        for req_file in ['requirements.txt', 'requirements_ui.txt']:
            if os.path.exists(req_file):
                with open(req_file, 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            package = line.split('>=')[0].strip()
                            try:
                                __import__(package.replace('-', '_').lower())
                            except ImportError:
                                missing_deps.append(line.strip())

        if missing_deps:
            print(f"   ⚠️  Dependencias faltantes: {', '.join(missing_deps)}")
            response = input("   ¿Instalar dependencias faltantes? (s/n): ")
            if response.lower() == 's':
                for dep in missing_deps:
                    subprocess.run([sys.executable, "-m", "pip", "install", dep])
        else:
            print("   ✓ Todas las dependencias instaladas")

    def create_assets(self):
        """Crea assets necesarios si no existen"""
        print("🎨 Preparando assets...")

        # Crear icono temporal si no existe
        icon_path = os.path.join(ASSETS_DIR, 'icon.ico')
        if not os.path.exists(icon_path):
            print("   ⚠️  Icono no encontrado. Creando icono temporal...")
            # Aquí normalmente generarías un icono real
            # Por ahora, creamos un archivo vacío como placeholder
            Path(icon_path).touch()

        # Crear otros assets necesarios
        for asset in ['splash.png', 'logo.png', 'file_icon.ico']:
            asset_path = os.path.join(ASSETS_DIR, asset)
            if not os.path.exists(asset_path):
                Path(asset_path).touch()
                print(f"   ✓ Creado placeholder: {asset}")

    def generate_spec_file(self):
        """Genera el archivo .spec para PyInstaller"""
        print("📝 Generando archivo de especificación...")

        # Preparar datos adicionales
        datas = []
        for src, dst in PYINSTALLER_CONFIG['add_data']:
            datas.append(f"('{src}', '{dst}')")
        datas_str = ',\n             '.join(datas)

        # Preparar imports ocultos
        hiddenimports = [f"'{imp}'" for imp in PYINSTALLER_CONFIG['hidden_imports']]
        hiddenimports_str = ',\n                     '.join(hiddenimports)

        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[{datas_str}],
    hiddenimports=[{hiddenimports_str}],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes={PYINSTALLER_CONFIG['exclude_module']},
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{PYINSTALLER_CONFIG['name']}',
    debug={self.debug},
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=not {PYINSTALLER_CONFIG['windowed']},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{PYINSTALLER_CONFIG['icon']}'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{PYINSTALLER_CONFIG['name']}'
)
"""

        with open(self.spec_file, 'w') as f:
            f.write(spec_content)
        print(f"   ✓ Generado: {self.spec_file}")

    def build_executable(self):
        """Construye el ejecutable usando PyInstaller"""
        print("🔨 Construyendo ejecutable...")

        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            self.spec_file
        ]

        if self.debug:
            cmd.append("--debug=all")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("   ✓ Construcción exitosa")
        else:
            print("   ❌ Error en la construcción:")
            print(result.stderr)
            sys.exit(1)

    def create_installer(self):
        """Crea el instalador para Windows"""
        if self.platform != 'windows':
            print("⚠️  Instalador solo disponible para Windows")
            return

        print("📦 Creando instalador...")

        # Crear script NSIS
        nsis_script = f"""
!define APP_NAME "{APP_NAME}"
!define APP_VERSION "{APP_VERSION}"
!define APP_PUBLISHER "{APP_AUTHOR}"
!define APP_URL "{APP_URL}"
!define APP_EXE "{PYINSTALLER_CONFIG['name']}.exe"

Name "${{APP_NAME}} ${{APP_VERSION}}"
OutFile "..\{PYINSTALLER_CONFIG['name']}_Setup_${{APP_VERSION}}.exe"
InstallDir "$PROGRAMFILES\${{APP_NAME}}"
InstallDirRegKey HKLM "Software\${{APP_NAME}}" "Install_Dir"

RequestExecutionLevel admin

!include "MUI2.nsh"

!define MUI_ABORTWARNING
!define MUI_ICON "{PYINSTALLER_CONFIG['icon']}"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "{INSTALLER_CONFIG['license_file']}"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "Spanish"

Section "Principal"
  SetOutPath $INSTDIR

  File /r "dist\{PYINSTALLER_CONFIG['name']}\*.*"

  WriteRegStr HKLM "Software\${{APP_NAME}}" "Install_Dir" "$INSTDIR"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${{APP_NAME}}" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${{APP_NAME}}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${{APP_NAME}}" "NoRepair" 1

  WriteUninstaller "uninstall.exe"

  CreateDirectory "$SMPROGRAMS\${{APP_NAME}}"
  CreateShortcut "$SMPROGRAMS\${{APP_NAME}}\${{APP_NAME}}.lnk" "$INSTDIR\${{APP_EXE}}"
  CreateShortcut "$DESKTOP\${{APP_NAME}}.lnk" "$INSTDIR\${{APP_EXE}}"
SectionEnd

Section "Uninstall"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${{APP_NAME}}"
  DeleteRegKey HKLM "Software\${{APP_NAME}}"

  Delete "$INSTDIR\*.*"
  RMDir /r "$INSTDIR"

  Delete "$SMPROGRAMS\${{APP_NAME}}\*.*"
  RMDir "$SMPROGRAMS\${{APP_NAME}}"
  Delete "$DESKTOP\${{APP_NAME}}.lnk"
SectionEnd
"""

        nsis_file = os.path.join(BUILD_DIR, 'installer.nsi')
        with open(nsis_file, 'w') as f:
            f.write(nsis_script)

        print(f"   ✓ Script NSIS creado: {nsis_file}")
        print("   ℹ️  Para crear el instalador, ejecuta NSIS con el script generado")

    def create_portable_zip(self):
        """Crea una versión portable en ZIP"""
        print("🗜️ Creando versión portable...")

        dist_folder = os.path.join(DIST_DIR, PYINSTALLER_CONFIG['name'])
        zip_name = f"{PYINSTALLER_CONFIG['name']}_Portable_{APP_VERSION}"

        shutil.make_archive(
            os.path.join(DIST_DIR, zip_name),
            'zip',
            dist_folder
        )

        print(f"   ✓ Creado: {zip_name}.zip")

    def run_tests(self):
        """Ejecuta tests básicos en el ejecutable"""
        print("🧪 Ejecutando tests...")

        exe_path = os.path.join(DIST_DIR, PYINSTALLER_CONFIG['name'], f"{PYINSTALLER_CONFIG['name']}.exe")

        if os.path.exists(exe_path):
            # Test básico: verificar que el ejecutable se puede ejecutar
            result = subprocess.run([exe_path, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("   ✓ Ejecutable funciona correctamente")
            else:
                print("   ⚠️  El ejecutable se creó pero puede tener problemas")
        else:
            print("   ❌ No se encontró el ejecutable")

    def build(self):
        """Proceso completo de construcción"""
        print(f"\n🚀 Iniciando construcción de {APP_NAME} v{APP_VERSION}")
        print("=" * 60)

        self.clean_build()
        self.create_directories()
        self.check_dependencies()
        self.create_assets()
        self.generate_spec_file()
        self.build_executable()

        if self.platform == 'windows':
            self.create_installer()

        self.create_portable_zip()
        self.run_tests()

        print("\n✅ Construcción completada exitosamente!")
        print(f"📁 Archivos generados en: {DIST_DIR}")


def main():
    parser = argparse.ArgumentParser(description='Constructor de Meeting Assistant Pro')
    parser.add_argument('--platform', choices=['windows', 'macos', 'linux'], 
                       default='windows', help='Plataforma objetivo')
    parser.add_argument('--debug', action='store_true', 
                       help='Construir en modo debug')
    parser.add_argument('--clean', action='store_true', 
                       help='Solo limpiar archivos de construcción')

    args = parser.parse_args()

    builder = MeetingAssistantBuilder(platform=args.platform, debug=args.debug)

    if args.clean:
        builder.clean_build()
    else:
        builder.build()


if __name__ == '__main__':
    main()
