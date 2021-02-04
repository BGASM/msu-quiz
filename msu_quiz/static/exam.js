const apiEndpoint = '/api/';
const url = '/exam';

// Register a global custom directive called `v-blur` that prevents focus




app = Vue.createApp({
  delimiters: ['[[', ']]'],
  data() {
    return {
      curr: 0,
      myexams: null,
      graded_exam: {},
      isActive: false,
      flascard: false,
      endofexam: false,
      issubmit: false,
      immediate: false

    }
  },
  provide() {
    return {
      exam_questions: Vue.computed(() => this.myexams),
      graded_exam: Vue.computed(() => this.graded_exam)
    }
  },
  async created() {
    const gResponse = await fetch(apiEndpoint + 'get_exam');
    const gObject = await gResponse.json();
    const exam_id = gObject.exam_data.id
    this.myexams = gObject.exam_data.exam_questions

    for (exam of this.myexams) {
      this.graded_exam[exam.question_no] = {
        'question': exam.question.id,
        'answer': exam.question.answer,
        choices: [],
        'selected': ''
      }
      for (mc of exam.mcq_list) {
        mc.mc['isActive'] = false;
        mc.mc['isCorrect'] = false;
        this.graded_exam[exam.question_no].choices.push(mc.mc.id)
      }
    }
    this.graded_exam['exam_id'] = exam_id
  },
  computed: {
    refreshQuestion: function() {
      return this.myexams[this.curr]
    }
  },

  methods: {
    updatequestion(e) {
      this.curr = --e
      if (this.flashcard) {
          this.immediate = false
      }
    },
    toggleActive(toggle) {
      this.flashcard = toggle
      this.isActive = true
    },
    ahead(event) {
      if (this.curr < this.myexams.length - 1) {
        this.curr++
        this.endofexam = false
      } else if (this.curr == this.myexams.length - 1) {
        this.endofexam = true
      }
    },
    behind(event) {
      if (this.curr > 0) {
        this.curr--
        this.endofexam = false
      }
    },
    submit(event) {
      if (this.curr > 0) {
        this.issubmit = true
      }
    },
      flashahead(event) {
        if (this.immediate) {
            this.immediate=false
            this.ahead()
        } else {
            this.immediate = true
        }
      },
    async posthome() {
      const exResponse = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        redirect: 'follow',
        body: JSON.stringify(this.graded_exam)
      });
      const exObject = await exResponse.json();
      window.location.href = exObject;
    }
  }
})

app.directive('blur', {
    mounted(el, binding) {
        el.onfocus = (ev) => ev.target.blur()
    }
})

app.component('buttonquestion', {
  delimiters: ['[[', ']]'],
  props: ['buttontext'],
  methods: {
    passquestion(buttontext) {
      this.$emit('updatequestion', buttontext)
    }
  },
  template: `
<button @click="passquestion(buttontext)"
type="button"
class="btn btn-link btn-sm"
id="[[ buttontext ]]"
data-test_no="[[ buttontext ]]">
[[ buttontext ]]
</button>`
})

app.component('question-return', {
  delimiters: ['[[', ']]'],
  inject: ['exam_questions', 'graded_exam'],
  props: ['qno', 'question', 'mcqs', 'answer', 'flashcard', 'immediate'],
  methods: {
    mcselected(id) {
      var tmp = this.qno
      var mclist = []
      for (mc of this.exam_questions.value[tmp - 1].mcq_list) {
        if (mc.mc.id == id) {
          mc.mc.isActive = true
          var choice = mc.mc.mcq
        } else {
          mc.mc.isActive = false
        }
        mclist.push(mc.mc.id)
      }
      this.graded_exam.value[tmp].selected = choice
    }
  },
  template: `  
  <h1 class="display-6">Question: [[ qno ]]</h1>
  <p class="lead">[[ question ]]</p>
  <hr class="my-4">
  <form>
         <div class="form-group list-group">
            <div> 
                <div v-for="mc in mcqs ">
                        <mcqbutton :mc="mc.mc" :answer="answer" :flashcard="flashcard" :immediate="immediate" @mcselected="mcselected"></mcqbutton>
                </div>
            </div>
        </div>
    </form>`
})

app.component('mcqbutton', {
  delimiters: ['[[', ']]'],
  props: ['mc', 'answer', 'flashcard', 'immediate'],
  methods: {
    selected(id) {
      this.$emit('mcselected', id)
    }
  },
  computed: {
    mcqClass: function() {
        if (this.immediate) {
            switch (this.mc.mcq) {
                case this.answer:
                    return 'list-group-item-success'
                    break;
                default:
                    return  (this.mc.isActive ? 'list-group-item-danger' : 'list-group-item')
            }
        } else {
            return {active: this.mc.isActive}
            }
        }
    },

  template: `
    <div class="form-check">  
    <a href="#"
    class="list-group-item list-group-item-action"
    name="mcq"
    :key="mc.id"
    :class="mcqClass"
    @click="selected(mc.id)">
    [[ mc.mcq ]]</a>
    </div>`
})

app.component('quiznavigation', {
  delimiters: ['[[', ']]'],
  emits: ['ahead', 'behind', 'submit', 'flashahead'],
  props: ['flashcard', 'endofexam', 'immediate'],
  methods: {
    control(controller) {
      this.$emit(controller)
    },
    selected(id) {
      this.$emit('mcselected', id)
    }
  },
  template: `                
    <div class="btn-group d-flex justify-content-center" role="group" id="btn-group" v-if="!flashcard">
        <button v-blur @click="control('behind')" class="btn btn-primary" type="button" value="Previous">
        Previous
        </button>
        <button v-blur @click="control('ahead')" class="btn btn-primary" type="button" value="Next" v-if="!endofexam">
        Next
        </button>
        <button v-blur v-if="endofexam" @click="control('submit')" type="button" id="submitbutton" class="btn btn-primary" data-toggle="modal" data-target="#submitModal">
        Submit
        </button>
    </div>
    <div class="btn-group d-flex justify-content-center" role="group" id="btn-group" v-if="flashcard">
        <button v-blur @click="control('flashahead')" class="btn btn-primary" type="button" value="Next">
        Next
        </button>
        <button v-blur @click="control('submit')" type="button" id="submitbutton" class="btn btn-primary" v-if="endofexam && immediate" data-toggle="modal" data-target="#submitModal">>
        Finish
        </button>
    </div>
    `
})

app.mount('#vue-template')