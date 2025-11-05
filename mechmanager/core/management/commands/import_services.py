# app/oficina/management/commands/import_services.py
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
import csv

from core.models import Service 

class Command(BaseCommand):
    help = "Importa serviços a partir de um CSV (category, service_name, price_min_brl, price_max_brl, estimated_hours)."

    def add_arguments(self, parser):
        parser.add_argument("--path", required=True, help="Caminho do CSV gerado")

    @transaction.atomic
    def handle(self, *args, **opts):
        path = opts["path"]
        created = 0
        updated = 0

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["service_name"].strip()
                # Define um preço padrão (ex.: média entre min e max)
                pmin = Decimal(str(row["price_min_brl"] or "0"))
                pmax = Decimal(str(row["price_max_brl"] or "0"))
                default_price = (pmin + pmax) / Decimal("2") if pmax > 0 else pmin

                # Converte horas -> minutos
                hours = Decimal(str(row["estimated_hours"] or "0"))
                estimated_minutes = int(hours * 60)

                obj, was_created = Service.objects.update_or_create(
                    name=name,
                    defaults={
                        "default_price": default_price,
                        "estimated_minutes": estimated_minutes,
                        "is_active": True,
                        "description": row.get("category", ""),  # opcional: guarda a categoria na descrição
                    },
                )
                created += int(was_created)
                updated += int(not was_created)

        self.stdout.write(self.style.SUCCESS(
            f"Import concluído. Criados: {created}, Atualizados: {updated}"
        ))
