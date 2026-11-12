<ol class="process-grid"><?php $stepCounter=0; foreach([
    ['chat','Tell us the problem','Show us what takes time, gets missed or is difficult to manage.'],
    ['plan','Agree on the plan','We define the features, cost, timeline and responsibilities before work starts.'],
    ['prototype','See your software take shape','Review working screens and give feedback as we build.'],
    ['test','Try it with real tasks','We check the important steps and fix issues before launch.'],
    ['rocket','Launch & get started','We agree on handover, guidance and any ongoing support you need.']
] as [$iconName,$h,$p]):?><li><div class="process-meta"><span class="process-icon"><?=icon($iconName)?></span><span class="step-number">0<?=++$stepCounter?></span></div><h3><?=$h?></h3><p><?=$p?></p></li><?php endforeach;?></ol>
