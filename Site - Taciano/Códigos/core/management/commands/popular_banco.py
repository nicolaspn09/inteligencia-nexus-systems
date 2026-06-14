# core/management/commands/popular_banco.py
import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from core.models import Lutador, Academia, Faixa, Modalidade, HistoricoGraduacao

class Command(BaseCommand):
    help = 'Popula o banco de dados com os registros de Kickboxing via CSV'

    def handle(self, *args, **kwargs):
        caminho_dados = os.path.join(settings.BASE_DIR, 'dados_csv')
        
        if not os.path.exists(caminho_dados):
            self.stdout.write(self.style.ERROR(f"Pasta não encontrada: {caminho_dados}. Crie a pasta e coloque os CSVs lá."))
            return

        # 1. Preparar Modalidade e Academia Padrão
        modalidade, _ = Modalidade.objects.get_or_create(
            nome='Kickboxing', 
            defaults={'descricao': 'Importado do sistema legado'}
        )
        
        academia_padrao, _ = Academia.objects.get_or_create(
            nome='Sem Academia/Desconhecida',
            defaults={'endereco': 'Não informado'}
        )

        # Mapeamento dos arquivos para a Ordem da Faixa
        arquivos = [
            ('Registro de GraduaçãoKickboxing_2025_2026.xlsx - Faixa-Laranja.csv', 'Laranja', 1),
            ('Registro de GraduaçãoKickboxing_2025_2026.xlsx - Faixa-Azul.csv', 'Azul', 2),
            ('Registro de GraduaçãoKickboxing_2025_2026.xlsx - Faixa-Amarela.csv', 'Amarela', 3),
            ('Registro de GraduaçãoKickboxing_2025_2026.xlsx - Faixa-Verde.csv', 'Verde', 4),
            ('Registro de GraduaçãoKickboxing_2025_2026.xlsx - Faixa-Marrom.csv', 'Marrom', 5),
            ('Registro de GraduaçãoKickboxing_2025_2026.xlsx - Faixa-Preta.csv', 'Preta 1º Dan', 6),
        ]

        for nome_arquivo, nome_faixa, ordem in arquivos:
            caminho_arquivo = os.path.join(caminho_dados, nome_arquivo)
            
            if not os.path.exists(caminho_arquivo):
                self.stdout.write(self.style.WARNING(f"Arquivo não encontrado, pulando: {nome_arquivo}"))
                continue

            faixa_obj, _ = Faixa.objects.get_or_create(nome=nome_faixa, defaults={'ordem': ordem})

            with open(caminho_arquivo, mode='r', encoding='utf-8-sig') as arquivo_csv:
                leitor = csv.reader(arquivo_csv)
                
                # Pula a linha de título inútil (Registro de Graduação...)
                next(leitor, None) 
                
                # Lê os cabeçalhos reais e limpa os espaços
                cabecalhos = next(leitor, None)
                if not cabecalhos:
                    continue
                cabecalhos = [c.strip().lower() for c in cabecalhos]

                # Descobre o índice das colunas independente do erro de digitação ("Academia" ou "Academias")
                idx_nome = cabecalhos.index('nome') if 'nome' in cabecalhos else 0
                idx_data = cabecalhos.index('data') if 'data' in cabecalhos else 3
                
                idx_academia = -1
                if 'academia' in cabecalhos:
                    idx_academia = cabecalhos.index('academia')
                elif 'academias' in cabecalhos:
                    idx_academia = cabecalhos.index('academias')

                for linha in leitor:
                    if not linha or not linha[idx_nome].strip():
                        continue # Pula linhas vazias
                    
                    nome_lutador = linha[idx_nome].strip()
                    str_data = linha[idx_data].strip() if len(linha) > idx_data else ''
                    nome_academia = linha[idx_academia].strip() if idx_academia != -1 and len(linha) > idx_academia else ''

                    # Tratamento da Academia
                    if nome_academia:
                        academia_obj, _ = Academia.objects.get_or_create(
                            nome=nome_academia,
                            defaults={'endereco': 'Endereço não cadastrado no CSV'}
                        )
                    else:
                        academia_obj = academia_padrao

                    # Tratamento de Data Vazia
                    data_graduacao = None
                    if str_data:
                        try:
                            # Tenta converter do padrão YYYY-MM-DD
                            data_graduacao = datetime.strptime(str_data, '%Y-%m-%d').date()
                        except ValueError:
                            pass
                    
                    if not data_graduacao:
                        data_graduacao = datetime.today().date() # Preenche com a data de hoje se falhar para não quebrar o banco

                    # Cria o Lutador
                    lutador_obj, created = Lutador.objects.get_or_create(
                        nome=nome_lutador,
                        defaults={
                            'academia': academia_obj,
                            'faixa_atual': faixa_obj
                        }
                    )
                    lutador_obj.modalidades.add(modalidade)

                    # Se a faixa da planilha for maior que a atual do banco, atualiza.
                    if lutador_obj.faixa_atual.ordem < faixa_obj.ordem:
                        lutador_obj.faixa_atual = faixa_obj
                        lutador_obj.save()

                    # Cria o Histórico
                    HistoricoGraduacao.objects.get_or_create(
                        lutador=lutador_obj,
                        faixa=faixa_obj,
                        defaults={
                            'data_graduacao': data_graduacao,
                            'examinador': 'Importado via CSV'
                        }
                    )

            self.stdout.write(self.style.SUCCESS(f"Faixa {nome_faixa} importada com sucesso!"))

        self.stdout.write(self.style.SUCCESS("Migração de dados finalizada."))