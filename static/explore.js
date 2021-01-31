const types = ['INFP', 'INTJ', 'INFJ', 'INTP', 'ENFP', 'ENTJ', 'ENTP', 'ENFJ', 'ISFJ', 'ISFP', 'ISTJ', 'ISTP', 'ESFJ', 'ESFP', 'ESTJ', 'ESTP'];
var unames;

const render_unames = (id) => {
  document.getElementById('unames').textContent = '';
  unames.forEach((person)=>{
    if(person.mbti === id){
      var list_element = document.createElement('div');
      list_element.textContent = person.uname;
      list_element.className = "list_element"
      document.getElementById('unames').appendChild(list_element);
    };
  })
};

const make_active = (e) => {
  types.forEach((type)=>{
    if(e.id != type){
      document.getElementById(type).className = "link";
    }
  });
  e.className = 'active';
  render_unames(e.id);
};

  document.body.onload = () =>
  {
    req = $.ajax({
        url : '/explore-data',
        type: 'POST',
      });

    req.done(function(data){
      unames = data;
      make_active(document.getElementById('INTJ'));
      });
  }
