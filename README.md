#NewsPaper(shell)
user1 =User.objects.create_user('Tim')      
user2 = User.objects.create_user('Tom') 

author1 = Author.objects.create(user=user1) 
author2 = Author.objects.create(user=user2)

cat1 = Category.objects.create(name = 'cat1')         
cat2 = Category.objects.create(name = 'cat2')  
cat3 = Category.objects.create(name = 'cat3')     
cat4 = Category.objects.create(name = 'cat4')  

post1 = Post.objects.create(post_type ='AR' , author= author1)
post2 = Post.objects.create(post_type ='AR' , author= author1)
post3 = Post.objects.create(post_type ='NW' , author= author2)

pc1 = PostCategory.objects.create(post=post1, category = cat1)
pc1_1 = PostCategory.objects.create(post=post1, category = cat3)
pc2 = PostCategory.objects.create(post=post2, category = cat4)
pc3 = PostCategory.objects.create(post=post3, category = cat2)


com1 = Comment.objects.create(text='Hello World', post=post1, user=user1)
com1_1 = Comment.objects.create(text='Hello Guys', post=post1, user=user2)
com2 = Comment.objects.create(text='Привет Мир', post=post2, user=user1)
com3 = Comment.objects.create(text='Пиво Hobos, для заказа пишите в лс)', post=post3, user=user2)

post1.like()
post1.like()
post1.like()
post2.dislike()
post3.like()
com1.like()
com1_1.dislike()
com2.dislike()
com3.like()

author1.update_rating()
author2.update_rating()

author1.rating
author2.rating

best_post = Post.objects.order_by('-rating').first()
best_post
best_post.rating

best_user_post = Comment.objects.filter(post=Post.objects.order_by('-rating').first()).values('date_in','user__username','rating','text')
