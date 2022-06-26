# Created by Sazhod at 23.06.2022
import csv


class Base:
    def __init__(self, name):
        self.name = name


class Status(Base):
    pass


class Brand(Base):
    pass


class Cateogry(Base):
    pass


class Product:
    def __init__(self, article, name, brand, status, category, volume, weight, availability, price, retailProductLink):
        self.article = article
        self.name = name
        self.brand = brand
        self.status = status
        self.category = category
        self.volume = volume
        self.weight = weight
        self.availability = availability
        self.price = price
        self.retailProductLink = retailProductLink


def fillingLists(bf, item, spec):
    for i in bf.filter(item, spec):
        if i:
            return False
    return True


def getData(path):
    productList = list()
    brandsList = list()
    statusesList = list()
    categoriesList = list()
    with open(path, newline='', encoding='utf-8') as csvfile:
        products = csv.reader(csvfile, delimiter=';')

        for p in list(products)[1:]:

            brand = Brand(name=p[6])
            status = Status(name=p[7])
            category = Cateogry(name=p[13])

            bf = BetterFilter()
            bs = BrandSpecification(brand)
            ss = StatusSpecification(status)
            cs = CategorySpecification(category)

            if fillingLists(bf, brandsList, bs):
                brandsList.append(brand)
            if fillingLists(bf, statusesList, ss):
                statusesList.append(status)
            if fillingLists(bf, categoriesList, cs):
                categoriesList.append(category)

            productList.append(
                Product(
                    article=p[0],
                    name=p[5],
                    brand=brand,
                    status=status,
                    category=category,
                    volume=p[14],
                    weight=p[15],
                    availability=p[16],
                    price=p[22],
                    retailProductLink=p[25]
                )
            )
        return {
            'products': productList,
            'brands': brandsList,
            'statuses': statusesList,
            'categories': categoriesList
        }


class Specification:
    def is_satisfied(self, item):
        pass


class Filter:
    def filter(self, items, spec):
        pass


class ProductCategorySpecification(Specification):
    def __init__(self, category):
        self.category = category

    def is_satisfied(self, item):
        return item.category.name == self.category.name


class CategorySpecification(Specification):
    def __init__(self, category):
        self.category = category

    def is_satisfied(self, item):
        return item.name == self.category.name


class ProductBrandSpecification(Specification):
    def __init__(self, brand):
        self.brand = brand

    def is_satisfied(self, item):
        return item.brand.name == self.brand.name


class BrandSpecification(Specification):
    def __init__(self, brand):
        self.brand = brand

    def is_satisfied(self, item):
        return item.name == self.brand.name


class ProductStatusSpecification(Specification):
    def __init__(self, status):
        self.status = status

    def is_satisfied(self, item):
        return item.status.name == self.status.name


class StatusSpecification(Specification):
    def __init__(self, status):
        self.status = status

    def is_satisfied(self, item):
        return item.name == self.status.name


class BetterFilter(Filter):
    def filter(self, items, spec):
        for item in items:
            if spec.is_satisfied(item):
                yield item


if __name__ == "__main__":
    """
    Проверка работоспособности OCP
    """

    product1 = Product(1, "test1", Brand("brand1"), Status("status1"), Cateogry("category1"), 1, 1, 1, 10, "none")
    product2 = Product(2, "test2", Brand("brand2"), Status("status1"), Cateogry("category1"), 1, 1, 1, 10, "none")
    product3 = Product(3, "test3", Brand("brand1"), Status("status2"), Cateogry("category2"), 2, 2, 2, 5, "none")

    products = [product1, product2, product3]

    bf = BetterFilter()

    category2 = ProductCategorySpecification(Cateogry("category2"))
    category = ProductCategorySpecification(Cateogry("category2"))
    for p in bf.filter(products, category2):
        print(p.name, p.category.name)
