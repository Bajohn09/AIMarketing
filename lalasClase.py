import os
import yaml
import json
import requests
from typing import Optional, Dict
from dataclasses import dataclass, asdict
from datetime import datetime
from dotenv import load_dotenv

@dataclass
class GenerateAudioResponse:
    """
    Dataclass para estructurar la respuesta de la API.
    Ventajas:
    - Validación automática de tipos
    - Acceso fácil a los datos como propiedades
    - Representación clara al imprimir
    """
    success: bool
    message: str
    task_id: str
    conversion_id_1: str
    conversion_id_2: str
    eta: int
    
    def to_dict(self):
        """Convierte la respuesta a diccionario"""
        return asdict(self)
    
    def to_txt_format(self) -> str:
        """Formatea la respuesta para guardar en txt"""
        return f"""
    
Respuesta de Lalas API:
----------------------
Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Éxito: {self.success}
Mensaje: {self.message}
ID de tarea: {self.task_id}
ID de conversión 1: {self.conversion_id_1}
ID de conversión 2: {self.conversion_id_2}
Tiempo estimado: {self.eta} segundos
----------------------
"""

class Configuration:
    def __init__(self):
        config_fn = os.getenv('CONFIG_FILE')
        
        with open(config_fn) as cf:
            self.config_file = yaml.safe_load(cf)
                        
    def get_prompt_path(self):
        return self.config_file.get("prompt_file", "")

    def get_lyrics_path(self):
        return self.config_file.get("lyrics_file", "")
       
        
class LalasAPI:
    def __init__(self, env_path: str = ".env"):
        """
        Inicializa el cliente de la API de Lalas.
        
        Args:
            env_path (str): Ruta al archivo .env que contiene la API key
        """
        load_dotenv(env_path)
        self.api_key = os.getenv('LALAS_API_KEY')
        if not self.api_key:
            raise ValueError("No se encontró LALAS_API_KEY en el archivo .env")
        
        self.base_url = "https://api.lalals.com/api/public/v1"
        self.headers = {
            'accept': 'application/json',
            'Authorization': self.api_key
        }

    def read_prompt_from_file(self, file_path: str) -> str:
        """
        Lee el prompt desde un archivo de texto.
        
        Args:
            file_path (str): Ruta al archivo txt que contiene el prompt
            
        Returns:
            str: Contenido del prompt
        """
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo de prompt: {file_path}")

    def save_response(self, response: GenerateAudioResponse, output_dir: str = "responses"):
        """
        Guarda la respuesta en archivos txt y json.
        
        Args:
            response: La respuesta de la API
            output_dir: Directorio donde guardar las respuestas
        """
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar nombre base del archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"lalas_response_{timestamp}"
        
        # Guardar en formato TXT
        txt_path = os.path.join(output_dir, f"{base_filename}.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(response.to_txt_format())
            
        # Guardar en formato JSON para procesamiento posterior si es necesario
        json_path = os.path.join(output_dir, f"{base_filename}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(response.to_dict(), f, indent=2)
            
        return txt_path, json_path

    def generate_audio(self, 
                      prompt_file: str,
                      music_style: str = "",
                      webhook_url: str = "http://api.lalals.com",
                      lyrics: str = "",
                      voice_id: str = "Drake",
                      save_response_files: bool = True) -> GenerateAudioResponse:
        """
        Genera audio usando la API de Lalas.
        
        Args:
            prompt_file (str): Ruta al archivo que contiene el prompt
            music_style (str, optional): Estilo musical deseado
            webhook_url (str, optional): URL para webhooks
            lyrics (str, optional): Letra de la canción
            voice_id (str, optional): ID de la voz a utilizar
            save_response_files (bool): Si se debe guardar la respuesta en archivos
            
        Returns:
            GenerateAudioResponse: Respuesta de la API
        """
        prompt = self.read_prompt_from_file(prompt_file)
        
        payload = {
            "prompt": prompt,
            "music_style": music_style,
            "webhook_url": webhook_url,
            "lyrics": lyrics,
            "voice_id": voice_id
        }

        response = requests.post(
            f"{self.base_url}/MusicAI",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"Error en la API: {response.status_code} - {response.text}")
            
        data = response.json()
        api_response = GenerateAudioResponse(**data)
        
        if save_response_files:
            txt_path, json_path = self.save_response(api_response)
            print(f"Respuesta guardada en:\n- TXT: {txt_path}\n- JSON: {json_path}")
            
        return api_response
    
    def retrieve_audio(self, task_id="a72c79d7-0800-41ba-a527-17e79e46cb4f", conversion_type="MUSIC_AI"):
        
        payload = {"task_id": "c53d8f7c-ec0d-44ce-bca0-d437d426556c",
                   "conversionType": conversion_type}
        
        response = requests.get(
            f"{self.base_url}/byId",
            headers=self.headers,
            params=payload)
        
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            Exception(f"Error en la API: {response.status_code} - {response.text}")
        

# Ejemplo de uso
if __name__ == "__main__":
    # Crear una instancia del cliente
    client = LalasAPI()
    
    # Crear una instancia de configuracion
    config = Configuration()
    prompt_path = config.get_prompt_path()
    
    #print(prompt_path)
    
    audio_response = client.retrieve_audio()
        
    """
    try:
        # Generar audio usando un prompt desde un archivo
        response = client.generate_audio(
            prompt_file=prompt_path,
            voice_id="Drake",
            save_response_files=True  # Esto guardará la respuesta automáticamente
        )
        
        print("\nRespuesta de la API:")
        print(response.to_txt_format())
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    """

    
    
 