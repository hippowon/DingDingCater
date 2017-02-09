KindEditor.ready(function(K) {
        K.create('textarea[name=content]',{
            width:'800px',
            height:'600px',
            uploadJson: 'admin/uploads/blogfile/',
            allowImageUpload:true,
        });
});