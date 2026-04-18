import json

path = 'd:\\MESTRADO\\1\u00ba Ano\\2\u00ba Semestre\\IAG\\IAG_TP1\\gan copy.ipynb'

with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] != 'code':
        continue
    src = cell['source']
    new_src = []
    i = 0
    while i < len(src):
        line = src[i]
        stripped = line.rstrip('\n')
        # Remove old commented lr line
        if stripped == '#lr = 0.0002':
            i += 1
            continue
        # Replace lr = 1e-4 with lr_G and lr_D
        if stripped == 'lr = 1e-4':
            new_src.append('lr_G = 2e-4  # Generator LR (>= lr_D)\n')
            new_src.append('lr_D = 1e-4  # Discriminator LR\n')
            i += 1
            continue
        # Fix optimizerD
        if 'optimizerD' in line and 'lr=lr,' in line:
            line = line.replace('lr=lr,', 'lr=lr_D,')
        elif 'optimizerD' in line and 'lr=lr)' in line:
            line = line.replace('lr=lr)', 'lr=lr_D)')
        # Fix optimizerG
        if 'optimizerG' in line and 'lr=lr,' in line:
            line = line.replace('lr=lr,', 'lr=lr_G,')
        elif 'optimizerG' in line and 'lr=lr)' in line:
            line = line.replace('lr=lr)', 'lr=lr_G)')
        new_src.append(line)
        i += 1
    cell['source'] = new_src

with open(path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print('Done')
