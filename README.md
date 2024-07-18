以MDN Web DocS中，用Django來建一個簡單圖書館的[教學](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django "Link")為基礎，建立一個簡易的訂購網頁。
<br>

以使用者端來看主要的功能與[version 1](https://github.com/ChuanYenWu/django_learning "Link")大同小異，在使用上沒太大變化。不過在管理者方面，進行物品的增減和修改會輕鬆許多。

### UML Association
![UML Association](/images/UML_association.png "index")<br>

將原先資料庫中儲存品項、訂單2種model的形式，改成Product(品項)、Order(訂單)、OrderItem(某品項訂購量)共3種model<br>
* Product: 所販賣的物品及定價
* Order: 訂單基本資訊
* **OrderItem**: 某筆訂單中，某個品項的訂購數量

改成此形式後，一個Order本身會含有多個OrderItem(若在一個訂單中訂購了不同品項的東西)；而某個Product可能存在於多個OrderItem中(若多筆訂單中都有訂購此品項)。<br>

和version 1相比，當我們新增品項時，不需要在Order model中增加該品項的欄位，而是藉由view.py和html表單的for loop來讓訂購者能看到新的Product欄位，至於是否訂購和訂購數量，則會由OrderItem儲存。如此一來管理者新增物品時，就不用對程式進行修改。
