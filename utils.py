import time
import logging
from functools import wraps
from typing import TypeVar, Callable, Any
import random

T = TypeVar('T')

def retry_with_backoff(
    retries: int = 3,
    backoff_in_seconds: int = 1,
    max_backoff_in_seconds: int = 30,
    exponential_base: int = 2,
    jitter: bool = True
) -> Callable:
    """
    Decorator para implementar retry pattern com backoff exponencial
    
    Args:
        retries: Número máximo de tentativas
        backoff_in_seconds: Tempo inicial de espera entre tentativas
        max_backoff_in_seconds: Tempo máximo de espera entre tentativas
        exponential_base: Base para o cálculo do backoff exponencial
        jitter: Se deve adicionar variação aleatória no tempo de espera
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            
            for retry in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if retry == retries - 1:
                        logging.error(f"Todas as {retries} tentativas falharam para {func.__name__}")
                        raise last_exception
                    
                    # Calcula o tempo de espera com backoff exponencial
                    wait_time = min(
                        max_backoff_in_seconds,
                        backoff_in_seconds * (exponential_base ** retry)
                    )
                    
                    # Adiciona jitter (variação aleatória) se configurado
                    if jitter:
                        wait_time = wait_time * (1 + random.random())
                    
                    logging.warning(
                        f"Tentativa {retry + 1} falhou para {func.__name__}. "
                        f"Erro: {str(e)}. "
                        f"Aguardando {wait_time:.2f}s antes da próxima tentativa."
                    )
                    
                    time.sleep(wait_time)
            
            return None  # Nunca deve chegar aqui devido ao raise anterior
            
        return wrapper
    return decorator

def wait_for_condition(
    condition: Callable[[], bool],
    timeout: int = 30,
    interval: float = 0.5,
    description: str = "condição"
) -> bool:
    """
    Aguarda até que uma condição seja verdadeira ou timeout seja atingido
    
    Args:
        condition: Função que retorna bool indicando se condição foi atingida
        timeout: Tempo máximo de espera em segundos
        interval: Intervalo entre verificações em segundos
        description: Descrição da condição para logs
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if condition():
            logging.debug(f"{description} atingida após {time.time() - start_time:.2f}s")
            return True
            
        time.sleep(interval)
    
    logging.error(f"Timeout aguardando por {description} após {timeout}s")
    return False

class Cache:
    """Cache simples com tempo de expiração"""
    
    def __init__(self, ttl_seconds: int = 300):
        self._cache = {}
        self._ttl = ttl_seconds
    
    def get(self, key: str) -> Any:
        """Obtém valor do cache se ainda válido"""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp <= self._ttl:
                logging.debug(f"Cache hit para chave: {key}")
                return value
            else:
                logging.debug(f"Cache expirado para chave: {key}")
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Armazena valor no cache com timestamp atual"""
        self._cache[key] = (value, time.time())
        logging.debug(f"Valor armazenado no cache para chave: {key}")
    
    def clear(self) -> None:
        """Limpa o cache"""
        self._cache.clear()
        logging.debug("Cache limpo") 