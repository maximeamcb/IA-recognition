import os
from PIL import Image

FIXED_SIZE = (20, 20)
THRESHOLD = 128


def load_image(path):
    return Image.open(path)


def convert_to_grayscale(img):
    return img.convert("L")


def binarize(img, threshold=THRESHOLD):
    width, height = img.size
    pixels = img.load()

    binary_img = Image.new("L", (width, height))
    binary_pixels = binary_img.load()

    for y in range(height):
        for x in range(width):
            binary_pixels[x, y] = 0 if pixels[x, y] < threshold else 255

    return binary_img


def crop_to_digit(img):
    width, height = img.size
    pixels = img.load()

    min_x = width
    min_y = height
    max_x = -1
    max_y = -1

    for y in range(height):
        for x in range(width):
            if pixels[x, y] == 0:
                if x < min_x:
                    min_x = x
                if y < min_y:
                    min_y = y
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y

    if max_x == -1 or max_y == -1:
        return img

    return img.crop((min_x, min_y, max_x + 1, max_y + 1))


def resize_image(img, size=FIXED_SIZE):
    return img.resize(size)


def image_to_matrix(img):
    width, height = img.size
    pixels = img.load()
    matrix = []

    for y in range(height):
        row = []
        for x in range(width):
            row.append(0 if pixels[x, y] == 0 else 1)
        matrix.append(row)

    return matrix


def matrix_to_vector(matrix):
    vector = []
    for row in matrix:
        for value in row:
            vector.append(value)
    return vector


def preprocess_image(path):
    img = load_image(path)
    img = convert_to_grayscale(img)
    img = binarize(img)
    img = crop_to_digit(img)
    img = resize_image(img)
    return img


def compare_vectors(v1, v2):
    score = 0

    for i in range(len(v1)):
        if v1[i] == v2[i]:
            if v1[i] == 0:
                score += 3
            else:
                score += 1

    return score


def build_dataset(reference_folder="reference"):
    dataset = {}

    for digit in range(10):
        dataset[digit] = []
        digit_folder = os.path.join(reference_folder, str(digit))

        if not os.path.isdir(digit_folder):
            print(f"Dossier manquant : {digit_folder}")
            continue

        for filename in os.listdir(digit_folder):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(digit_folder, filename)
                img = preprocess_image(path)
                matrix = image_to_matrix(img)
                vector = matrix_to_vector(matrix)
                dataset[digit].append(vector)

        print(f"Digit {digit}: {len(dataset[digit])} example(s) loaded")

    return dataset


def find_test_image():
    possible_names = [
        "Chiffre.png",
        "Chiffre.jpeg",
        "Chiffre.jpg",
        "chiffre.png",
        "chiffre.jpeg",
        "chiffre.jpg",
    ]

    for name in possible_names:
        if os.path.exists(name):
            return name

    return None


def recognize_digit(test_image_path, dataset):
    test_img = preprocess_image(test_image_path)
    test_matrix = image_to_matrix(test_img)
    test_vector = matrix_to_vector(test_matrix)

    best_digit = None
    best_score = -1

    for digit, examples in dataset.items():
        for example_vector in examples:
            score = compare_vectors(test_vector, example_vector)
            print(f"Comparison with digit {digit}: score = {score}")

            if score > best_score:
                best_score = score
                best_digit = digit

    return best_digit, best_score, test_matrix


def print_matrix(matrix):
    print("\nPixel matrix:")
    for row in matrix:
        print(" ".join(str(value) for value in row))


def main():
    test_image = find_test_image()

    if test_image is None:
        print("Aucune image test trouvée.")
        return

    print(f"Image test utilisée : {test_image}")

    dataset = build_dataset("reference")
    total_examples = sum(len(examples) for examples in dataset.values())

    if total_examples == 0:
        print("Aucune image de référence trouvée dans le dataset.")
        return

    digit, score, matrix = recognize_digit(test_image, dataset)

    print_matrix(matrix)
    print()
    print(f"Chiffre reconnu : {digit}")
    print(f"Meilleur score : {score}")


if __name__ == "__main__":
    main()