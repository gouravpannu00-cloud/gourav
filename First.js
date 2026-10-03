console.log("Gourav Pannu");
console.log("GOURAV PANNU");
//console.log("PANNU");  THIS  IS  A COMMENT

          //  OPERATORS_______________________________

let a = 10 ;
let b = 5 ;
console.log("a + b = ",a + b);
console.log("a - b = ",a - b);
console.log("a * b = ",a * b);
console.log("a / b = ", a / b);
console.log("a % b = ",a % b);      // remainder jo bachaga wo show hoga
console.log("a ** b =", a ** b);   // a ki power b

// 5 ka multiple h ya nhi

let num = prompt("enter a number = ");

if (num % 5 === 0) {
    console.log(num," is multiple of 5 ");
} else {
    console.log(num," is not multiple of 5");
}

//   give grade to students 

let score = prompt("Enter a Score = ");

if (score >= 90 && score <= 100) {
    console.log(score ," = A  GRADE ");
} else if (score >= 70 && score <= 89) {
    console.log(score ," = B  GRADE");
} else if (score >= 60 && score <= 69 ) {
    console.log(score , "= C GRADE")
} else if (score >= 50 && score <= 59){
    console.log(score , "=  D  GRADE ");
} else if (score >= 0 && score <= 49) {
    console.log(score , " = F  GRADE " )
}

