from django.contrib.auth.models import User
from rest_framework import status
from store.models import Collection, Product
import pytest
from model_bakery import baker


@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post('/store/collections/', collection)
    return do_create_collection

@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self, api_client, create_collection):
        response = create_collection({'title': 'a'})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, create_collection):
        authenticate(is_staff=False)

        response = create_collection({'title': 'a'})
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, authenticate, create_collection):
        authenticate(is_staff=True)

        response = create_collection({'title': ''})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_data_is_valid_returns_201(self, authenticate, create_collection):
        authenticate(is_staff=True)

        response = create_collection({'title': 'a'})
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exists_returns_200(self, api_client):
        #Arrange
        collection = baker.make(Collection)
        
        response = api_client.get(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': collection.id,
            'title': collection.title,
            'products_count': 0
        }

    def test_if_collection_not_found_returns_404(self, api_client):
        response = api_client.get('/store/collections/999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND



@pytest.mark.django_db
class TestListCollections:
    def test_if_collections_exist_returns_200(self, api_client):
        baker.make(Collection, _quantity=5)

        response = api_client.get('/store/collections/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5



@pytest.mark.django_db
class TestUpdateCollection:
    def test_if_user_is_admin_can_update(self, authenticate, api_client):
        authenticate(is_staff=True)
        collection = baker.make(Collection)

        response = api_client.patch(
            f'/store/collections/{collection.id}/',
            {'title': 'updated'}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'updated'


@pytest.mark.django_db
class TestDeleteCollection:
    def test_if_user_is_admin_can_delete(self, authenticate, api_client):
        authenticate(is_staff=True)
        collection = baker.make(Collection)

        response = api_client.delete(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT


######## Product Tests ########

@pytest.mark.django_db
class TestCreateProduct:
    def test_if_data_is_valid_returns_201(self, authenticate, api_client):
        authenticate(is_staff=True)
        collection = baker.make(Collection)

        response = api_client.post('/store/products/', {
            'title': 'Product A',
            'slug': 'product-a',
            'unit_price': 10,
            'inventory': 5,
            'collection': collection.id
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

    def test_if_data_is_invalid_returns_400(self, authenticate, api_client):
        authenticate(is_staff=True)

        response = api_client.post('/store/products/', {
            'title': '',
            'slug': '',
            'unit_price': 0,
            'inventory': -1
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_if_user_is_not_admin_returns_403(self, authenticate, api_client):
        authenticate(is_staff=False)

        collection = baker.make(Collection)

        response = api_client.post('/store/products/', {
            'title': 'Product A',
            'slug': 'product-a',
            'unit_price': 10,
            'inventory': 5,
            'collection': collection.id
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_anonymous_returns_401(self, api_client):
        collection = baker.make(Collection)

        response = api_client.post('/store/products/', {
            'title': 'Product A',
            'slug': 'product-a',
            'unit_price': 10,
            'inventory': 5,
            'collection': collection.id
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRetrieveProduct:
    def test_if_product_exists_returns_200(self, api_client):
        product = baker.make(Product)

        response = api_client.get(f'/store/products/{product.id}/')

        assert response.status_code == status.HTTP_200_OK

    def test_if_product_not_found_returns_404(self, api_client):
        response = api_client.get('/store/products/999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestListProducts:
    def test_if_products_exist_returns_200(self, api_client):
        baker.make(Product, _quantity=5)

        response = api_client.get('/store/products/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 5
        assert len(response.data['results']) == 5


@pytest.mark.django_db
class TestDeleteProduct:
    def test_if_admin_can_delete_product(self, authenticate, api_client):
        authenticate(is_staff=True)
        product = baker.make(Product)

        response = api_client.delete(f'/store/products/{product.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT




