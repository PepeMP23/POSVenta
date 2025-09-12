# ProyectoTienda Django

## Descripción

**ProyectoTienda** es una aplicación de comercio electrónico desarrollada con Django, diseñada para gestionar comercios, productos, usuarios y ventas de manera eficiente.

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalados los siguientes programas en tu sistema:

* **Python 3.12.10** o superior.
* **Git** para clonar el repositorio.

## Instalación

Sigue estos pasos para configurar y ejecutar el proyecto en tu máquina local:

1.  **Clonar el repositorio:** Abre tu terminal y ejecuta el siguiente comando para descargar el código.

    ```bash
    git clone [https://github.com/carlabastida/reingenieriaPOS.git](https://github.com/carlabastida/reingenieriaPOS.git)
    cd ProyectoTienda
    ```

2.  **Crear y activar el entorno virtual:** Es crucial crear un entorno virtual para aislar las dependencias del proyecto.

    ```bash
    # Crear entorno virtual env
    python -m env myworld

    # Ejecuutar entorno virtual
    # En Windows:
    env\Scripts\activate.bat
    # En macOS/Linux:
    source env/bin/activate
    ```

3.  **Instalar dependencias:** Con el entorno virtual activado, instala todas las librerías necesarias desde el archivo `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

## Configuración de la Base de Datos

El archivo SQL crea la base de datos, mientras que las migraciones se encargarán de crear las tablas necesarias para la aplicación.

1.  **Crear la base de datos:** La aplicación utiliza MySQL, ejecuta el script SQL que se encuentra en la raíz del proyecto para crear la base de datos vacía.

    ```bash
    # Ejemplo para MySQL:
    mysql -u tu_usuario -p < base_de_datos.sql
    ```
2. **Agregar tu usuario y contraseña en settings.py:** Se deben agregar en el archivo settings.py, en USER tu usuario de acceso a mysql y en PASSWORD tu contraseña

    ```bash
    # En el archivo de settings.py busca la siguiente sección
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'BarrioStore',
        'USER': 'root',
        'PASSWORD': 'root1',
        'HOST':'localhost',
        'PORT':'3306',
        }
    }
    ```

3.  **Aplicar las migraciones:** Este comando creará todas las tablas y relaciones definidas en los modelos de Django.

    ```bash
    python manage.py migrate
    ```

## Creación de un Superusuario

Para acceder al panel de administración de Django y gestionar el contenido de la tienda, es necesario crear un superusuario. Ojo: El super usuario no es necesario pero lo puedes crear para ver el administrador de django.

1.  **Ejecutar el comando `createsuperuser`:** Sigue las instrucciones en la terminal para definir un nombre de usuario, correo electrónico y contraseña.

    ```bash
    python manage.py createsuperuser
    ```

## Ejecución del Proyecto

1.  **Ejecutar el servidor de desarrollo:**

    ```bash
    python manage.py runserver
    ```

2.  **Acceder a la aplicación:** La aplicación estará disponible en tu navegador en la siguiente dirección:

    ```
    [http://127.0.0.1:8000/tienda](http://127.0.0.1:8000/tienda)
    ```
    Al momento de acceder, abrir la pagina del login, deberas registrar un usuario para comenzar, te recomiendo vendor para que puedas visualizar tiendas desde otro usuario customer

    Puedes acceder al panel de administración de Django en `http://127.0.0.1:8000/admin`.

#  Tienda Online

Este proyecto es una aplicación web de una tienda online que permite a usuarios registrados actuar como **clientes** o **vendedores** según su rol asignado.

---

## 🚀 Funcionalidades

###  Roles de Usuario
- **Admin**: Puede gestionar usuarios y productos.  
- **Vendedor**: Puede gestionar su tienda, productos, y ver sus ventas.  
- **Cliente**: Puede ver tiendas y productos, agregar productos al carrito, realizar compras, y ver su historial de pedidos.  

---

### 📌 Funcionalidades Principales

####  Registro y Autenticación
- Los usuarios pueden registrarse como **clientes** o **vendedores**.  
- Inicio de sesión autenticado según el rol del usuario.  

####  Clientes
- Ver listado de tiendas y productos.  
- Añadir productos al carrito y proceder al checkout para realizar compras.  
- Ver historial de pedidos.  

####  Vendedores
- Gestionar su tienda: crear, editar y actualizar información.  
- Gestionar productos: agregar, editar y eliminar productos.  
- Ver su perfil de vendedor y estadísticas de ventas.  

####  Administradores
- Gestionar usuarios: crear, editar y eliminar usuarios.  
- Gestionar productos globalmente: crear, editar y eliminar productos de todas las tiendas.  

---

###  Seguridad
- Acceso restringido a vistas según el rol del usuario.  
- Redireccionamiento adecuado al intentar acceder a vistas no autorizadas.  
- Gestión de errores **404 personalizados** para vistas no encontradas.  

---

## 🗄️ Modelos

###  Usuario (User)
- **Campos**: `username`, `email`, `role` (choices: *customer*, *vendor*, *admin*), `created_at`, `image_url`.  

###  Tienda (Store)
- **Campos**: `name`, `description`, `address`, `google_maps_link`, `email`, `user (FK a User)`, `created_at`, `image_url`.  

###  Producto (Product)
- **Campos**: `name`, `description`, `price`, `stock`, `store (FK a Store)`, `category`.  

###  Carrito de Compras (ShoppingCart) y Ítems del Carrito (CartItem)
- Modelos para gestionar productos en el carrito antes de realizar una compra.  

###  Pedidos (Orders) e Ítems de Pedido (OrderItem)
- Modelos para gestionar pedidos y productos asociados a cada pedido.  

###  Promociones (Promotion)
- Modelos para gestionar promociones aplicadas a productos.  

---

## 🎨 Diseño Funcional


### 🖼️ Vistas Principales
- **Inicio (`store_list`)**: Listado de tiendas y productos.  
- **Detalle de Producto (`product_detail`)**: Información detallada de un producto específico.  
- **Carrito de Compras (`cart_view`)**: Vista del carrito con productos seleccionados.  
- **Checkout (`checkout_views`)**: Proceso de compra con ingreso de datos de envío y pago.  
- **Historial de Pedidos (`order_history`)**: Vista para clientes para ver sus pedidos anteriores.  
- **Gestión de Tienda (`manage_store`)**: Vista para vendedores para gestionar su tienda.  
- **Gestión de Productos (`vendor_products`)**: Vista para vendedores para gestionar sus productos.  
- **Perfil de Vendedor (`vendor_profile`)**: Información estática de la tienda del vendedor.  
- **Panel de Vendedor (`vendorHome`)**: Dashboard del vendedor con enlaces a gestionar tienda, productos y perfil.  

---
