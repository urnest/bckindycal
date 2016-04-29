$(document).ready(function(){
  tinymce.init({
    selector: 'div.kindycal-py-links',
    inline: true,
    plugins: [
      'advlist autolink lists link image2 charmap print preview anchor',
      'searchreplace visualblocks code fullscreen',
      'insertdatetime media table contextmenu paste code upload_doc'
    ],
    toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image2'
  });
  $('input#save-button').click(function(){
    var linksPageContent=$('div.kindycal-py-links').html();
    if (!$('input#save-button').hasClass('kc-busy-cursor')){
      $('input#save-button').addClass('kc-busy-cursor');
      kc.postToServer('save_links_page_content',{
	params:kc.json.encode({
	  newContent:linksPageContent
	})
      })
	.always(function(){
	  $('input#save-button').removeClass('kc-busy-cursor');
	});
    }
    return false;
  });
  $('body').removeClass('kc-invisible');//added by kindycal.py
})
