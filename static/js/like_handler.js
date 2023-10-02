$(document).ready(function() {
    $(".like-button").click(function() {
      var itemSlug = $(this).data("item-slug");
      var likeButton = $(this); // Lưu trữ nút "like" vào biến để dễ thao tác
      var liked = likeButton.hasClass("liked");
      var likeUrl = $("#data-like-url").data("like-url");
      // Gửi yêu cầu POST để xử lý yêu thích
      $.ajax({
        type: "POST",
        url: likeUrl,
        data: {
          item_slug: itemSlug,
          liked : liked ? 'False' : 'True',
          csrfmiddlewaretoken: "{{ csrf_token }}"
        },
        success: function(data) {
          // Đảm bảo thay đổi màu sắc của nút "like"
          if (liked) {
            likeButton.removeClass("liked text-danger");
            likeButton.html("Like <i class=\"fas fa-thumbs-up m-1\"></i>")
          } else {
            likeButton.addClass("liked text-danger");
            likeButton.html("Liked <i class=\"fas fa-thumbs-up m-1\"></i>")
          }
        }
      });
    });
});
