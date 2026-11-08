"""Tratamento de imagem para capas com qualidade baixa (fotos de origem pequenas ou muito comprimidas).
Alisa o "quadriculado" de compressão JPEG nas áreas lisas e recupera nitidez só nos contornos
(letras, silhuetas), sem realçar ruído. Não muda enquadramento, tamanho, cores nem tom.
Uso: python3 site/melhorar_capa.py site/assets/img/capas/<slug>.jpg [...]   (sobrescreve o arquivo)
     python3 site/melhorar_capa.py --forca 1.3 arquivo.jpg                  (mais nitidez; padrão 1.0)"""
import sys
import cv2
import numpy as np


def melhorar(img, forca=1.0):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    L = lab[..., 0]
    # mapa de contornos: onde há bordas reais (letras, silhuetas), não textura/ruído
    suave = cv2.GaussianBlur(L, (0, 0), 1.5)
    gx, gy = cv2.Sobel(suave, cv2.CV_32F, 1, 0), cv2.Sobel(suave, cv2.CV_32F, 0, 1)
    mag = cv2.GaussianBlur(np.sqrt(gx * gx + gy * gy), (0, 0), 2)
    borda = np.clip((mag - 6) / 30, 0, 1)
    # áreas lisas: alisa de leve o quadriculado da compressão JPEG
    L_liso = cv2.GaussianBlur(L, (0, 0), 0.9)
    base = L * borda + L_liso * (1 - borda) * 0.6 + L * (1 - borda) * 0.4
    # bordas: nitidez com limite (sem contorno branco)
    d = np.clip((L - cv2.GaussianBlur(L, (0, 0), 1.4)) * 0.9 * forca, -14, 14)
    lab[..., 0] = np.clip(base + d * borda, 0, 255)
    # cores e tom ficam como estavam
    return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)


if __name__ == "__main__":
    args = sys.argv[1:]
    forca = 1.0
    if args[:1] == ["--forca"]:
        forca = float(args[1]); args = args[2:]
    for f in args:
        img = cv2.imread(f)
        if img is None:
            print("Não abriu:", f); continue
        cv2.imwrite(f, melhorar(img, forca), [cv2.IMWRITE_JPEG_QUALITY, 92, cv2.IMWRITE_JPEG_PROGRESSIVE, 1])
        print("Tratada:", f)
