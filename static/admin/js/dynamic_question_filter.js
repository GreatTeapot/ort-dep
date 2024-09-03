(function($) {
    $(document).ready(function() {
        $('#id_topics').change(function() {
            var selectedTopicIds = $(this).val();
            $.ajax({
                url: '/admin/get_questions/',
                data: {
                    'topic_ids': selectedTopicIds
                },
                dataType: 'json',
                success: function(data) {
                    var questionsSelect = $('#id_testquestions_set-0-question');
                    questionsSelect.empty();
                    $.each(data.questions, function(index, question) {
                        questionsSelect.append($('<option>', {
                            value: question.id,
                            text: question.question_text
                        }));
                    });
                }
            });
        });
    });
})(django.jQuery);
