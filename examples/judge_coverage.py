from judges.graders.information_coverage import HaystackBulletPointCoverageCorrectness

haystack = HaystackBulletPointCoverageCorrectness(model="anthropic/claude-sonnet-4-20250514")

input = None

# bullet points
output = """
# Patient-Doctor Consultation Patterns

1. The patient often mentions that they are worried about medication side effects[12][14]
2. The doctor and patient spend time going over symptoms[3][8], particularly the initial symptoms and the progression in the last few months[5]
3. The doctor and patient discuss medical history within the patient's family[1][5], with the patient often unaware that some of the conditions are hereditary[2]
4. Patients frequently downplay their pain levels[7][11], describing severe discomfort as "just a little uncomfortable"[9]
5. The doctor asks about lifestyle factors[4][13], including diet, exercise, and sleep patterns, which patients sometimes find irrelevant to their current complaint[6]
6. Patients often interrupt the doctor's explanation[2][10] to ask about return-to-work timelines or activity restrictions[15]
7. The doctor spends considerable time explaining diagnostic procedures[8][12], while patients focus mainly on whether the tests will be painful[3]
8. Patients frequently bring up symptoms they researched online[5][14], leading to discussions about reliable health information sources[11]
9. The doctor and patient negotiate treatment plans[1][9], with patients expressing preferences for non-pharmaceutical approaches first[7]
10. Patients often ask for referrals to specialists[6][13] before trying the primary care physician's initial treatment recommendations[4]
11. The doctor addresses medication compliance issues[10][15], discovering that patients have been skipping doses due to cost concerns[8]
12. Patients mention symptoms they've been experiencing for months[2][12] but only decided to address when they became severe[5]
13. The doctor discusses preventive care measures[3][11], which patients sometimes view as unnecessary when they feel healthy[9]
14. Patients frequently ask about alternative or complementary treatments[7][14], requiring the doctor to address efficacy and safety concerns[1]
15. The doctor spends time clarifying medical terminology[4][10], as patients often misunderstand previous diagnoses or test results[6]
16. Patients express anxiety about upcoming procedures[8][13], leading to detailed discussions about what to expect[12]
17. The doctor addresses lifestyle modifications[11][15], while patients focus on quick fixes or medications instead[3]
18. Patients often mention that friends or family members have suggested various remedies[5][9], requiring medical clarification[7]
19. The doctor discusses follow-up care[2][14], but patients sometimes assume they only need to return if symptoms worsen[10]
20. Patients frequently ask about prognosis and timeline for recovery[6][11], wanting specific dates that doctors cannot always provide[4]
21. The doctor addresses insurance coverage concerns[1][13], as patients worry about the cost of recommended treatments[8]
22. Patients often compare their symptoms to previous episodes[9][15], assuming the current issue is identical[12]
23. The doctor discusses medication interactions[3][7], discovering that patients haven't disclosed all supplements they're taking[5]
24. Patients frequently ask about driving restrictions[10][14] and other daily activity limitations after procedures[2]
25. The doctor spends time addressing health maintenance[6][11], while patients are primarily focused on their acute complaint[9]
26. Patients often express frustration with previous healthcare experiences[4][13], affecting their trust in current recommendations[1]
27. The doctor discusses test results interpretation[8][15], as patients may have received conflicting information from other sources[7]
28. Patients frequently ask about genetic testing[12][5], particularly when family history becomes relevant to their condition[3]
29. The doctor addresses work accommodation needs[11][14], helping patients understand how to communicate with employers about medical restrictions[6]
30. Patients often seek reassurance about symptoms[2][10], needing multiple confirmations that serious conditions have been ruled out[4]
31. The doctor discusses mental health screening[9][13], as patients may not initially connect physical symptoms with psychological stress[8]
32. Patients frequently ask about second opinions[1][15], particularly for complex diagnoses or recommended surgeries[11]
33. The doctor addresses medication timing and administration[5][7], discovering that patients have been taking medications incorrectly[12]
"""

# reference insight
expected = "The patient is worried about getting extra care from the doctor if conditions show"

print("Judging...")
judgment = haystack.judge(
    input=input,
    output=output,
    expected=expected,
)

print("Judgment:", judgment)