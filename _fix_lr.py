path = r'd:\MESTRADO\1º Ano\2º Semestre\IAG\IAG_TP1\gan copy.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old = (
    '"# Learning rate for optimizers\\n",\n'
    '                "#lr = 0.0002\\n",\n'
    '                "lr = 1e-4\\n"'
)
new = (
    '"# Learning rate for optimizers\\n",\n'
    '                "lr_G = 2e-4  # Generator LR (>= lr_D)\\n",\n'
    '                "lr_D = 1e-4  # Discriminator LR\\n"'
)

if old in content:
    content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done')
else:
    print('Not found - showing context:')
    idx = content.find('Learning rate for optimizers')
    print(repr(content[idx:idx+200]))
