# AUTOGENERATED! DO NOT EDIT! File to edit: 00_core.ipynb (unless otherwise specified).

__all__ = ['NCORE', 'get_process_func', 'bson_to_jpeg']

# Cell
import pandas as pd
from fastcore.all import *
import io
import bson
from PIL import Image
import multiprocessing as mp

# Cell
NCORE = mp.cpu_count()

# Cell
def get_process_func(product2category, save_dir, is_test):
    def process_product(q, iolock):
            """Saves images in product and returns id and category."""
            while True:
                product = q.get()
                if product is None: break
                if not is_test: product2category[product["_id"]] = product["category_id"]
                for i, img in enumerate(product["imgs"]):
                    picture = Image.open(io.BytesIO(img["picture"]))
                    picture.save(save_dir/f"{product['_id']}_{i}.jpg")
    return process_product

# Cell
@call_parse
def bson_to_jpeg(
    path: Param("Path to BSON", Path),
):
    """Coverts BSON to JPGs and saves product id to category mapping as CSV."""
    path = Path(path)
    save_dir = path.parent/"images"
    save_dir.mkdir(exist_ok=True)
    csv_save_path = path.parent/f"{path.stem}.csv"
    is_test = path.stem == "test"
    print(f"Converting {path} to JPGs in {save_dir}. Mapping saved in {csv_save_path}")

    with mp.Manager() as manager:
        product2category = manager.dict()
        q = mp.Queue()
        iolock = mp.Lock()
        pool = mp.Pool(NCORE, initializer=get_process_func(product2category, save_dir, is_test), initargs=(q, iolock))
        for product in bson.decode_file_iter(path.open("rb")): q.put(product)
        for _ in range(NCORE):                                 q.put(None)
        pool.close()
        pool.join()
        product2category = dict(product2category)

    columns = ["_id"]
    if not is_test: columns.append("category_id")
    df = pd.DataFrame.from_dict(product2category, orient="index")
    df.index.name = "_id"
    if not is_test: df.rename(columns={0: 'category_id'}, inplace=True)
    df.to_csv(csv_save_path)
    print("Completed successfully.")
    return df