from django.db import models
from django.contrib.auth.models import User


# 전체 커뮤니티 + 보호소별 커뮤니티 공용 (shelter가 null이면 전체, 있으면 해당 보호소)
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="작성자")
    shelter = models.ForeignKey(
        'shelter.Shelter', on_delete=models.CASCADE, null=True, blank=True,
        verbose_name="보호소", related_name="community_posts"
    )
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "게시글"
        verbose_name_plural = "게시글"

    def __str__(self):
        return self.title
