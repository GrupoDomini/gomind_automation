"""Aqui estão todas as funções relacionadas a controle de mouse e teclado"""

from typing import Union
import pyautogui as py
from time import sleep, time
import os
import pyperclip
import pynput
import keyboard
import string


class Logger:
    def log(self, message, status="info"):
        print("{} - [{}]".format(message, status))


class ExceptionWithLog(Exception):
    def __init__(self, *args: object) -> None:
        print(*args)
        super().__init__(*args)


class FileDontExists(ExceptionWithLog):
    def __init__(self) -> None:
        super().__init__("Imagem nao existe")


_CAMINHO_IMG = os.path.join(".", "img")
_LOGGER = Logger()
_CONFIDENCE = 0.8


class Automation:
    """Utilizar essa classe para setar as variáveis do automation"""

    CAMINHO_IMG = _CAMINHO_IMG
    logger = _LOGGER
    CONFIDENCE = _CONFIDENCE

    def __init__(
        self,
        caminho_img: str = _CAMINHO_IMG,
        logger: any = _LOGGER,
        confidence: float = _CONFIDENCE,
    ) -> None:
        Automation.CAMINHO_IMG = caminho_img
        Automation.logger = logger
        Automation.CONFIDENCE = confidence


def pegar_caminho_da_imagem(nome_do_arquivo: str, usar_caminho_da_imagem: bool = True):
    CAMINHO_IMG = Automation.CAMINHO_IMG

    return (
        os.path.join(CAMINHO_IMG, nome_do_arquivo)
        if usar_caminho_da_imagem
        else nome_do_arquivo
    )


def encontrar_imagem(
    nome_do_arquivo: str,
    ignorar_erro: bool = False,
    confidence: float = Automation.CONFIDENCE,
    grayscale: bool = False,
    usar_caminho_da_imagem: bool = True,
):
    logger = Automation.logger
    logger.log("Tentando encontrar imagem {}".format(nome_do_arquivo))
    try:
        location = py.locateCenterOnScreen(
            pegar_caminho_da_imagem(nome_do_arquivo, usar_caminho_da_imagem),
            grayscale=grayscale,
            confidence=confidence,
        )  # type: ignore
        logger.log("Encontrou a imagem {}: ({}, {})".format(nome_do_arquivo, *location))
        return location
    except Exception as e:
        logger.log("Nao encontrou a imagem {}".format(nome_do_arquivo))
        if ignorar_erro:
            return False
        else:
            raise e


def esperar_imagem(
    arquivos: Union[str, list[str]],
    segundos: int = 10,
    intervalo: float = 0.5,
    confidence: float = Automation.CONFIDENCE,
    grayscale: bool = False,
    usar_caminho_da_imagem: bool = True,
):
    logger = Automation.logger
    start_time = time()

    if isinstance(arquivos, str):
        arquivos = [arquivos]

    while time() - start_time < segundos:
        try:
            for arquivo in arquivos:
                position = encontrar_imagem(
                    arquivo,
                    confidence=confidence,
                    grayscale=grayscale,
                    usar_caminho_da_imagem=usar_caminho_da_imagem,
                )
                if position is not None:
                    logger.log(f"Encontrou a imagem {arquivo}")
                    return position
        except Exception as _:
            pass
        sleep(intervalo)

    logger.log(f'Não encontrou nenhuma imagem: {" ".join(arquivos)}')

    return False


def esperar_imagem_sumir(
    arquivo: str,
    segundos: int = 10,
    intervalo: int = 1,
    confidence: float = Automation.CONFIDENCE,
    grayscale: bool = False,
    usar_caminho_da_imagem: bool = True,
):
    logger = Automation.logger
    if esperar_imagem(
        arquivo,
        segundos=20,  # Tempo de 20 segundos e intervalo de 1, se nao encontrar a imagem ele vai dar uma exception
        intervalo=1,
        grayscale=grayscale,
        confidence=confidence,
        usar_caminho_da_imagem=usar_caminho_da_imagem,
    ):
        start_time = time()
        while time() - start_time < segundos:
            posicao = encontrar_imagem(
                arquivo,
                grayscale=grayscale,
                confidence=confidence,
                ignorar_erro=True,
                usar_caminho_da_imagem=usar_caminho_da_imagem,
            )

            if not posicao:
                logger.log(f"A imagem {arquivo} ja sumiu")
                return True

            logger.log(f"A imagem {arquivo} nao sumiu ainda")
            sleep(intervalo)
    else:
        raise ExceptionWithLog(
            f"A imagem {arquivo} nao foi encontrada, ela precisa estar em tela para esperar sumir"
        )
    return False


def clicar_na_imagem_ate_sumir(
    arquivo: str,
    tentativas: int = 5,
    intervalo: float = 1,
    clicks=1,
    confidence: float = Automation.CONFIDENCE,
    grayscale: bool = False,
    usar_caminho_da_imagem: bool = True,
):
    logger = Automation.logger

    # Ele verifica se a imagem esta em tela para que ele possa clicar e esperar sumir
    if (
        primeiraPosicao := esperar_imagem(
            arquivo,
            segundos=20,  # Tempo de 20 segundos e intervalo de 1, se nao encontrar a imagem ele vai dar uma exception
            intervalo=1,
            grayscale=grayscale,
            confidence=confidence,
            usar_caminho_da_imagem=usar_caminho_da_imagem,
        )
    ):
        for i in range(tentativas):
            posicao = (
                encontrar_imagem(
                    arquivo,
                    grayscale=grayscale,
                    confidence=confidence,
                    ignorar_erro=True,
                    usar_caminho_da_imagem=usar_caminho_da_imagem,
                )
                if i != 0
                else primeiraPosicao
            )
            logger.log(f"Clicando na imagem {arquivo} ate sumir. tentativa = {i}")
            if not posicao:
                logger.log(f"A imagem {arquivo} ja sumiu")
                return True
            logger.log(f"A imagem {arquivo} nao sumiu ainda")
            py.click(posicao, clicks=clicks)
            sleep(intervalo)
    else:
        raise ExceptionWithLog(
            f"A imagem {arquivo} nao foi encontrada, ela precisa estar em tela para clicarmos ate sumir"
        )
    return False


def clicar_na_imagem(
    nome_do_arquivo: Union[str, list[str]],
    segundos: int = 10,
    intervalo: float = 0.5,
    confidence: float = Automation.CONFIDENCE,
    clicks: int = 1,
    intervalo_click: int = 0,
    grayscale: bool = False,
    usar_caminho_da_imagem: bool = True,
):
    """Essa funcao espera a imagem aparecer e entao clica nela"""
    if posicao := esperar_imagem(
        nome_do_arquivo,
        segundos,
        intervalo,
        confidence=confidence,
        grayscale=grayscale,
        usar_caminho_da_imagem=usar_caminho_da_imagem,
    ):
        py.click(posicao, clicks=clicks, interval=intervalo_click)
    else:
        raise ExceptionWithLog(f"Imagem {nome_do_arquivo} nao foi encontrada")


def clicar_no_centro_da_tela():
    width, height = py.size()
    py.doubleClick(width / 2, height / 2)


def mover_para_o_centro_da_tela():
    logger = Automation.logger
    width, height = py.size()
    logger.log("Width {}, Height {}".format(width, height))
    py.moveTo(width / 2, height / 2)


def special_write(texto: str) -> None:
    """
    Essa funcao escreve qualquer texto, precisamos disso pois o pyautogui nao consegue
    caracteres especiais.
    """
    pyperclip.copy(texto)
    sleep(0.5)
    py.hotkey("ctrl", "v")


def write(texto: str) -> None:
    """So consegue escrever coisas sem caracter especial."""
    py.write(texto)


class MouseControl:
    """
    Usage:
        import pyautogui
        import time

        MouseControl.start_block()
        for _ in range(5):
            py.moveTo(randint(200, 500), randint(200, 500), 1)
            sleep(0.5)
        MouseControl.stop_block()

    """

    mouse_listener = pynput.mouse.Listener(suppress=True)

    def start_block():
        MouseControl.mouse_listener.start()

    def stop_block():
        MouseControl.mouse_listener.stop()


KEYS_TO_BLOCK = list(string.ascii_lowercase + string.digits + string.punctuation) + [
    "tab",
    "shift",
    "enter",
    "ctrl",
]


class KeyboardControl:
    """
    Usage:
        import pyautogui
        import time


        KeyboardControl.start_block()


        def on_key_press(key):
            print(f"Key {key} pressed")


        KeyboardControl.add_listener(on_key_press).start()

        for key in KEYS_TO_BLOCK:
            print("Vai apertar o {}".format(key))
            pyautogui.press(key)
            time.sleep(0.5)

        KeyboardControl.stop_block()
    """

    listeners = []

    def start_block():
        for key in KEYS_TO_BLOCK:
            keyboard.block_key(key)

    def stop_block():
        for key in KEYS_TO_BLOCK:
            keyboard.unblock_key(key)

    def add_listener(def_to_listen):
        listener = pynput.keyboard.Listener(on_press=def_to_listen)
        KeyboardControl.listeners.append(listener)
        return listener
