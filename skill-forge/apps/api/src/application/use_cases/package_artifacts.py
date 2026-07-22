from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from src.domain.entities import GeneratedFile, Project, TargetAgent


def _usage_readme(agent: TargetAgent, suggested_prompt: str) -> str:
    return f"""# Como usar este SKILL/instructions no {agent.value}

1. Onde colocar o arquivo: siga os caminhos dos arquivos incluidos neste pacote.
2. Como o agente carrega: use o mecanismo nativo do agente (repo rules, system prompt, skill file).
3. Boas praticas: versione junto do codigo e atualize quando dominio/regras mudarem.

## Prompt sugerido para comecar a usar agora:

> {suggested_prompt}
"""


def package_as_zip(
    files: list[GeneratedFile],
    project: Project,
    agent: TargetAgent,
    suggested_prompt: str,
) -> bytes:
    stream = BytesIO()
    with ZipFile(stream, mode="w", compression=ZIP_DEFLATED) as zip_file:
        for generated in files:
            zip_file.writestr(generated.path, generated.content)

        zip_file.writestr("README_USO.md", _usage_readme(agent, suggested_prompt))
        zip_file.writestr("PROMPT_SUGERIDO.md", suggested_prompt)
        zip_file.writestr("PROJECT_SUMMARY.md", f"Projeto: {project.skill_name}\nObjetivo: {project.objective}\n")

    return stream.getvalue()
