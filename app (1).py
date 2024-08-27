from flask import Flask, request, jsonify, abort
import requests

app = Flask(__name__)

BASE_URL = "http://*******/test/companies/"

def get_auth_token():
    url = "http://*********/test/auth"
    data = {
        "companyName": "**********",
        "clientID": "********",
        "clientSecret": "*********",
        "ownerName": "**********",
        "ownerEmail": "*********",
        "rollNo": "***********"
    }
    
    response = requests.post(url, json=data)

    print(response.json())
    
    if 'access_token' in response.json():
        auth_data = response.json()
        return auth_data['access_token']
    else:
        raise Exception("Failed to obtain authorization token")

# Helper Function to make requests to the external API
def make_external_request(auth_token, company, category, n, min_price, max_price): 
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    url = f"{BASE_URL}{company}/categories/{category}/products"
    params = {"top": n, "minPrice": min_price, "maxPrice": max_price}
    response = requests.get(url, headers=headers, params=params)
    print(min_price)
    print(response)
    print(url)    
    print(response.status_code)
    if response.status_code != 200:
        abort(response.status_code)

    return response.json()

# Helper function to sort products
def sort_products(products, sort_key, sort_order):
    return sorted(products, key=lambda x: x[sort_key], reverse=(sort_order == "desc"))

# Helper function to generate unique product ID
def generate_product_id(product):
    return hash(product['productName'] + str(product['price']))

# Endpoint to get the top 'n' products within a category
@app.route('/categories/<string:categoryname>/products', methods=['GET'])
def get_top_products(categoryname):
    n = int(request.args.get('n', 10))
    page = int(request.args.get('page', 1))
    min_price = request.args.get('minPrice', 0)
    max_price = request.args.get('maxPrice', float('inf'))
    sort_key = request.args.get('sort', 'rating')
    sort_order = request.args.get('order', 'desc')
    
    company_list = ["AMZ", "FLP", "SNP", "MYN", "AZO"]
    all_products = []
    auth_token = get_auth_token()
    for company in company_list:
        products = make_external_request(auth_token, company, categoryname, n, min_price, max_price)
        all_products.extend(products)
    print(all_products)

    # Sorting products based on the sort_key and sort_order
    all_products = sort_products(all_products, sort_key, sort_order)

    print("Total products: ", len(all_products))
    # Implement pagination
    products_per_page = 10 * len(company_list)  # 10 products per company, so 50 products per page
    start_index = (page - 1) * products_per_page
    end_index = start_index + products_per_page

    paginated_products = all_products[start_index:end_index]

    # Adding unique ID to each product
    for product in paginated_products:
        product['id'] = generate_product_id(product)

    return jsonify(paginated_products)


# Endpoint to get product details by product ID
@app.route('/categories/<string:categoryname>/products/<int:productid>', methods=['GET'])
def get_product_by_id(categoryname, productid):
    company_list = ["AMZ", "FLP", "SNP", "MYN", "AZO"]
    auth_token = get_auth_token()

    for company in company_list:
        products = make_external_request(auth_token, company, categoryname, 10, 0, 5000)
        for product in products:
            if generate_product_id(product) == productid:
                return jsonify(product)
    
    abort(404, description="Product not found")

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)