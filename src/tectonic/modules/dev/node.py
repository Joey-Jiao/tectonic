import os

from tectonic import config
from tectonic.core import fs, process, ui


def activate_nvm() -> None:
    nvm_sh = config.DIR_NVM / "nvm.sh"
    if nvm_sh.exists():
        os.environ["NVM_DIR"] = str(config.DIR_NVM)
        process.run_shell(f'source "{nvm_sh}"')


def run() -> None:
    ui.section("Node.js Development Environment (NVM)")

    if config.DIR_NVM.exists():
        ui.info(f"NVM already installed at {config.DIR_NVM}")
        return

    fs.ensure_dir(config.DIR_NVM)

    ui.step("Installing NVM")
    # NVM_DIR must be set before running install.sh
    process.run_shell(f'''
        export NVM_DIR="{config.DIR_NVM}"
        curl -fsSL {config.URL_NVM_INSTALL} | bash
    ''')

    nvm_sh = config.DIR_NVM / "nvm.sh"
    if not nvm_sh.exists():
        ui.error("NVM installation failed")
        return

    ui.step("Installing latest LTS Node.js")
    process.run_shell(f'''
        export NVM_DIR="{config.DIR_NVM}"
        source "{nvm_sh}"
        nvm install --lts
        nvm use --lts
        nvm alias default 'lts/*'
    ''')

    ui.ok("NVM and Node.js installed")
