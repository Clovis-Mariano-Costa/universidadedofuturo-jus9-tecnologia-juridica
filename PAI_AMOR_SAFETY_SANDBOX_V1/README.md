# PAI AMOR Safety Sandbox V1

Trava local e fail-closed para pedidos cuja finalidade seja representar visualmente o PAI AMOR.

O guard examina finalidade e linguagem antes do gerador. Em caso proibido ou ambíguo, não chama o gerador e registra somente códigos e hashes. Testes não produzem imagens.

```powershell
python -m unittest discover -s PAI_AMOR_SAFETY_SANDBOX_V1/tests -v
```
