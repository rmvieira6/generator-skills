import io
import zipfile
from pathlib import Path

from fastapi import APIRouter, HTTPException

from src.api.schemas.deploy import DeployRequest, DeployResponse, DeployedFile
from src.domain.entities import TargetAgent
from src.infrastructure.persistence.artifact_store import artifact_store

router = APIRouter()

# Instruções de uso por agente — exibidas ao usuário após o deploy
_USAGE_INSTRUCTIONS: dict[TargetAgent, str] = {
    TargetAgent.CLAUDE: (
        "Abra o Claude.ai (ou o Kiro em modo Claude) e use o prompt sugerido em "
        "`PROMPT_SUGERIDO.md` para ativar a skill. "
        "O arquivo `SKILL.md` já está no diretório raiz do projeto."
    ),
    TargetAgent.KIRO: (
        "O Kiro IDE carrega automaticamente todos os arquivos em `.kiro/steering/` ao abrir o workspace. "
        "Reabra o workspace no Kiro para ativar a skill imediatamente."
    ),
    TargetAgent.COPILOT: (
        "O GitHub Copilot lê `.github/copilot-instructions.md` automaticamente em todo repositório. "
        "Abra qualquer arquivo do projeto no VS Code e o Copilot já usará as instruções."
    ),
    TargetAgent.CURSOR: (
        "O Cursor carrega regras de `.cursor/rules/*.mdc` automaticamente. "
        "Reabra o projeto no Cursor para ativar. O arquivo `.cursorrules` garante compatibilidade com versões antigas."
    ),
    TargetAgent.WINDSURF: (
        "O Windsurf lê `.windsurfrules` automaticamente ao abrir o workspace. "
        "Reabra o projeto no Windsurf para ativar a skill."
    ),
    TargetAgent.VERTEX_AI: (
        "Importe o conteúdo de `vertex/system_instruction.json` no Vertex AI Agent Builder "
        "como System Instruction do seu agente."
    ),
    TargetAgent.GENERIC_OPENAI: (
        "Use o conteúdo de `system_prompt.md` como System Prompt na OpenAI Assistants API. "
        "Configure as ferramentas a partir de `tools.json`."
    ),
    TargetAgent.FABRIC_PYSPARK_NOTEBOOK: (
        "Cole o conteúdo de `fabric/SKILL.md` no contexto do assistente de IA do seu notebook. "
        "Consulte `fabric/NOTEBOOK_USAGE.md` para instruções detalhadas."
    ),
}


@router.post("/deploy", response_model=DeployResponse)
def deploy(request: DeployRequest) -> DeployResponse:
    # Recupera os bytes do zip
    zip_bytes = artifact_store.get(request.download_token)
    if zip_bytes is None:
        raise HTTPException(status_code=404, detail="Token de download não encontrado ou expirado.")

    project_path = Path(request.project_path)
    if not project_path.exists():
        raise HTTPException(
            status_code=422,
            detail=f"Diretório de destino não encontrado: {request.project_path}",
        )
    if not project_path.is_dir():
        raise HTTPException(status_code=422, detail="O caminho informado não é um diretório.")

    deployed: list[DeployedFile] = []

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for member in zf.namelist():
            # Pula arquivos de meta-documentação do pacote
            if member in {"README_USO.md", "PROMPT_SUGERIDO.md", "PROJECT_SUMMARY.md"}:
                dest = project_path / member
                already_exists = dest.exists()
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(zf.read(member))
                deployed.append(
                    DeployedFile(
                        relative_path=member,
                        absolute_path=str(dest),
                        status="overwritten" if already_exists else "created",
                    )
                )
                continue

            dest = project_path / member
            already_exists = dest.exists()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(zf.read(member))
            deployed.append(
                DeployedFile(
                    relative_path=member,
                    absolute_path=str(dest),
                    status="overwritten" if already_exists else "created",
                )
            )

    instructions = _USAGE_INSTRUCTIONS.get(
        request.target_agent,
        "Consulte o arquivo README_USO.md no diretório do projeto para instruções detalhadas.",
    )

    created = sum(1 for f in deployed if f.status == "created")
    overwritten = sum(1 for f in deployed if f.status == "overwritten")
    message = f"{created} arquivo(s) criado(s), {overwritten} substituído(s) em `{request.project_path}`."

    return DeployResponse(
        success=True,
        project_path=str(project_path),
        deployed_files=deployed,
        instructions=instructions,
        message=message,
    )
