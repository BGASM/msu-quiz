const apiEndpoint = '/api/';
const url = '/exam';

app = Vue.createApp({
  delimiters: ['[[', ']]'],
  data() {
    return {
      exam_data: null,
      score: null,
      isActive: false
    }
  },

  async created() {
    const gResponse = await fetch(apiEndpoint + 'get_exam');
    const gObject = await gResponse.json();
    this.exam_data = gObject.exam_data;
    this.score = gObject.exam_data.score;
    this.isActive = true;
  }
})

app.component('score', {
  delimiters: ['[[', ']]'],
  props: ['score'],
  data() {
    return {
      passing: false
    }
  },
  created() {
    this.passing = this.score >= 70
  },
  template: `
  <h1 class="display-3">You scored: 
  <span 
  :class="passing ? 'text-success' : 'text-danger'"> [[ score ]]%
  </span>
  </h1>  
  <p class="lead">This is a prototype. In the future exam review will be similar to Examplify.</p>
`
})

app.component('exam_review', {
  delimiters: ['[[', ']]'],
  props: ['exam_questions'],
  template: `
    <div v-for="question of exam_questions">    
    <exam_review_question
    :qno="question.test_no"
    :question="question.question"
    :mcqs="question.mcq_order"
    :answer="question.answer"
    :selected="question.selected"
    :correct="question.correct"></exam_review_question>
</div>
`
})

app.component('exam_review_question', {
  delimiters: ['[[', ']]'],
  props: ['qno', 'question', 'mcqs', 'answer', 'selected', 'correct'],
  template: `
  <div class="card mb-3"
  :class="correct ? ' border-success' : 'border-danger'">
  <div class="card-header">
  [[ qno ]].
  </div> 
  <div class="card-body">
  <h5 class="card-title">
  [[ question ]]
  </h5>
  
  <ul class="list-group list-group-flush" v-for="mc of mcqs">
  <mcq 
  :mc="mc" 
  :answer="answer" 
  :selected="selected" 
  :correct="correct"></mcq>
  </ul> 
  </div>
  </div>
  `
})

app.component('mcq', {
  delimiters: ['[[', ']]'],
  props: ['mc', 'answer', 'selected', 'correct'],
  data() {
    return {
      mc_style: 'list-group-item-primary'
    }
  },
  created() {
    switch (this.mc) {
      case this.answer:
        this.mc_style = 'list-group-item-success'
        break;
      case this.selected:
        this.mc_style = 'list-group-item-danger'
        break;
      default:
        this.mc_style = 'list-group-item'
    }
  },
  template: `
  <li class="list-group-item"
  :class="[[mc_style]]">
  [[ mc ]]
  </li>
  `
})

app.mount('#results')