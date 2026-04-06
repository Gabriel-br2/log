import pytest
import shutil
import logging
from pathlib import Path

from log.logger import HandleDebug


@pytest.fixture(autouse=True)
def setup_and_teardown():
    HandleDebug._shared_state.clear()
    
    yield
    
    for path in Path(".").glob("LOG_*"):
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)


def test_singleton_behavior():
    log1 = HandleDebug("test_app")
    log2 = HandleDebug("other_name")
    
    assert log1.name == log2.name
    assert log1.logger is log2.logger
    assert log1.__dict__ is log2.__dict__


def test_format_string():
    log = HandleDebug("teste_fmt")
    
    assert log._format_string("Erro", "grave", 404) == "Erro grave 404"
    
    assert log._format_string(eixo=6, status="colisao") == "eixo=6 | status=colisao"
    
    resultado = log._format_string("Falha no robô", eixo=6, vel=100)
    assert resultado == "Falha no robô | eixo=6 | vel=100"


def test_file_creation():
    log = HandleDebug("teste_arquivo")
    
    caminho_log = Path(log.file_name)
    assert caminho_log.exists()
    assert caminho_log.is_file()
    assert caminho_log.parent.name == "LOG_pytest"


def test_flow_decorator():
    log = HandleDebug("teste_flow")
    
    @log.flow
    def soma(a, b):
        return a + b
        
    result = soma(5, 5)
    assert result == 10


def test_time_decorator():
    log = HandleDebug("teste_time")
    
    @log.time
    def multiplica(a, b):
        return a * b
        
    result = multiplica(3, 4)
    assert result == 12


def test_change_keep_log():
    log = HandleDebug("teste_retencao")
    assert log.keep_logs_for_days == 7 # Valor padrão
    
    log.change_keep_log(15)
    assert log.keep_logs_for_days == 15