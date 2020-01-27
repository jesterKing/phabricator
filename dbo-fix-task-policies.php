#!/usr/bin/env php 
<?php

//dev instance ids
//$NEW_POLICY_PHID = "PHID-PLCY-2ortrlhfgmxa6yqt3l2n";
//$AUTHOR_USERNAME = "blenderdev";

// Using policy as per object T73709 - chosen because
// policy changing has been hidden. Used the Conduit
// 'maniphest.gettasktransactions' and took policy
// PHID from it
$NEW_POLICY_PHID = "PHID-PLCY-635czvlvk7qfvuwe63wi";
$AUTHOR_USERNAME = "jesterking";

$root = dirname(__FILE__);
require_once $root.'/scripts/__init_script__.php';

echo pht("Running visibility policy check and revert.")."\n";

// Omnipotent user is neeeded to act out the policy change transactions.
$OMNIPOTENT = PhabricatorUser::getOmnipotentUser();

// User who is making the policy changes.
$author = id(new PhabricatorUser())
  ->loadOneWhere('username = %s', $AUTHOR_USERNAME);

$table = new ManiphestTask();
$tasks = id(new ManiphestTask())
  ->loadAllWhere('viewPolicy = %s OR editPolicy = %s', 'obj.maniphest.author', 'obj.maniphest.author');

function newContentSource() {
  return PhabricatorContentSource::newForSource(
      PhabricatorConsoleContentSource::SOURCECONST);
}

function setTaskPolicies($task, $policy) {
  global $OMNIPOTENT;
  global $author;

  $transactions[] = id(new ManiphestTransaction())
    ->setAuthorPHID($author->getPhid())
    ->setTransactionType(PhabricatorTransactions::TYPE_VIEW_POLICY)
    ->setNewValue('public');

  $transactions[] = id(new ManiphestTransaction())
    ->setAuthorPHID($author->getPhid())
    ->setTransactionType(PhabricatorTransactions::TYPE_EDIT_POLICY)
    ->setNewValue($policy);

  $content_source = newContentSource();

  $editor = id(new ManiphestTransactionEditor())
      ->setActor($OMNIPOTENT)
      ->setContentSource($content_source)
      ->setIsSilent(true)
      ->setContinueOnNoEffect(true);

  $editor->applyTransactions($task, $transactions);
}

foreach($tasks as $task)
{
  setTaskPolicies($task, $NEW_POLICY_PHID);
}

?>
