import os
import subprocess
from typing import Optional, Tuple
import logging

from aiohttp import web

stress_testing_a = os.environ.get('GENERATOR_PARAMETER_A')
stress_testing_b = os.environ.get('GENERATOR_PARAMETER_B')

TOKEN_GENERATOR_WASM_FILENAME = 'js_header_generator.wasm'
TOKEN_GENERATOR_JS_EXECUTABLE_FILENAME = 'js_executable'

def _run_generator_script(stress_testing_e: str) -> Tuple[Optional[str], Optional[str]]:
    clientvarresourselist, stress_testing = None, None

    script_dir = os.path.dirname(os.path.realpath(__file__))
    js_executable_file_path = os.path.join(script_dir, TOKEN_GENERATOR_JS_EXECUTABLE_FILENAME)
    wasm_file_path = os.path.join(script_dir, TOKEN_GENERATOR_WASM_FILENAME)

    try:
        result = subprocess.run(
            [
                js_executable_file_path,
                stress_testing_a,
                stress_testing_b,
                str(stress_testing_e),
                wasm_file_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        clientvarresourselist, stress_testing = result.stdout.split('\n')[:2]
    except subprocess.SubprocessError:
        logging.exception(
            f'Got error during generator script execution for {stress_testing_e=}'
        )
    except AttributeError:
        logging.exception(
            f'Error retrieving tokens from script execution result for {stress_testing_e=}'
        )
    except Exception:
        logging.exception(
            f'Got some error on generator script execution for {stress_testing_e=}'
        )

    return clientvarresourselist, stress_testing

async def handle_request(request):
    data = await request.json()
    stress_testing_e = data.get('stress_testing_e')

    if stress_testing_e is None:
        return web.Response(text='Missing stress_testing_e parameter', status=400)

    result = _run_generator_script(stress_testing_e)

    return web.json_response({'result': result})

app = web.Application()
app.router.add_post('/generate_tokens', handle_request)

if __name__ == "__main__":
    web.run_app(app)