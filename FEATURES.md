


Client (Mobil App, Whatsapp)

Clientin  2 görevi var, 
- chate istek atar ve ön tarafta sonucunu gösterir. 
- chate istek atmaz ama bazı planlanmış görevlerin sonucunu gösterir.


Backend 

Backend'e chat isteği clientten veya cronjoblar veya bir trigger tarafından gönderildi. 3ü tarafından da aynı sonuç dönecek. yani burada bir seçici strateji yok. Koyabiliriz ama gerek yok bence hepsi aynı yere gidecek aynı şekilde. belki triggerların verdiği duyuruları mobil appde farklı bir sekmede gösterebiliriz. Veya cronjobları.

Backenddde elimizde
Burada chat isteğine nasıl gideceği ve bizim bilgiyi nasıl çekeceğimiz söz konusu aslında terimlerden  emin değilim
parantez içinde ( veri nasıl gelecek - chate nasıl gidecek ) olarak yazacağım veri kaynaklarına 

burada
trigger : çağırmamıza gerek olmadan. olay olduğu anda. 
cronjob : belirli aralıklarla çalışan
stable  : biz çağırmadıkça veri olduğu yerde kalacak. 

calling : veri çağırdığımız anda gelecek. her üçü için de geçerli.  

birden fazla veri kaynağı var.  
Bunlardan birkaçı şunlar olabilir: 

- Teams mesajları ( trigger- trigger)
- Yemekhane (cronjob - cronjob,calling )
- Akdeniz CSE websitesi (duyurular için cronjob-trigger veya izin alabilirsek trigger-trigger) 
                        (içerisindeki  bilgiler için  )
    -(tabi burada istediğimiz siteyi scrape edebilecegimiz şekilde bir mikroservis olmalı. ama izin olursa gerek kalmaz buna ilk etapta gerek yok.)
- Whatsapp mesajlarının kendisi (az sonra sebebini anlatacagim ) ( trigger - calling)
- Mobil uygulamadaki mesajlar ( Mobil uygulamaya da mesaj kısmı koyalım. Şuan whatsapptaki CSE topluluğunu komple oraya taşıyalım derim. bence bunu bitirmeye götürürüz.) (trigger)
- 
TAMAMLAYAMADIM KAFAM KARIŞTI GECE SİZDE İNCELEDİKTEN SONRA TARTIŞIRIZ. 


Senaryolar: 
- Opsys'te en son nereye kadar işlemiştik? | Shared memory system sanırım. @Ikbal öyle değil mi? (Daha önceki mesajlardan buldu ve kullanıcısı ile beraber yanıtı döndürdü. )
- algoda geçen hafta yoklama alındı mı? | Evet, alındı ( geçen haftaki mesajlardan öğrendi mesela bunu da)
- Stajda ne yapmam gerekiyordu bilen var mı? | Öncelikle ...... (Burada uzun uzun anlattı.  Akdeniz CSE sitesindeki staj bilgilerinden çektiğini anlattı. altına da kaynak belirtti.)
- Yemekte bugün ne var | (Yemeği söyler) (zaten cronjob olarak sabah paylaşıldı ama yine de göndermiş oldu sorulduğu için. )
- Teamsten hoca mesaj yazar. anında buraya mesaj olarak iletilir mesela.  










aklıma iki yaklaşım geldi bilemedim birini seçicez veya aklınıza başka bir şey geldiyse ekleyin secelim. 



                                                                                
TRIGGER  ---------|                                      - TOOL GET INFO -----> SET INFO RESOURCE  
CRONJOB  ---------| ----> |LLM|(ne yapmam isteniyor?)    - TOOL A
APICALL  ---------|                                      - TOOL B 




TRIGGER  ---------|                                      - TOOL GET INFO - 
CRONJOB  ---------| ----> |LLM|(ne yapmam isteniyor?)    - TOOL A
APICALL  ---------|                                      - TOOL B 
